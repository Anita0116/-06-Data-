import pandas as pd
import numpy as np 
from typing import Dict, NamedTuple

class Table(NamedTuple):
    df: pd.DataFrame
    schema: pd.DataFrame

def missing_value_analysis(df, tbl_name):
    missing_ratio = df.isnull().sum() / len(df) * 100
    missing_df = pd.DataFrame({
        '列名': missing_ratio.index,
        '缺失比例(%)': missing_ratio.values
    }).sort_values('缺失比例(%)', ascending=False)
    
    print(f"\n{tbl_name}缺失值统计：")
    print(missing_df[missing_df['缺失比例(%)'] > 0])
    return missing_df


def fill_missing_values(df):
    """
    NSCLC 专用缺失值填补策略（含 PDL1_TPS 的合理处理）
    """

    # ========= 1. 连续变量（中位数） =========
    cont_cols = ['TMB', 'Age', 'NLR', 'Albumin', 'OS_Months', 'PFS_Months']
    for col in cont_cols:
        if col in df.columns and df[col].isnull().sum() > 0:
            df[col].fillna(df[col].median(), inplace=True)

    # ========= 2. PDL1_TPS：按治疗方案分组填补（核心修改） =========
    if 'PDL1_TPS' in df.columns:
        # 合理范围约束
        df.loc[(df['PDL1_TPS'] < 0) | (df['PDL1_TPS'] > 100), 'PDL1_TPS'] = np.nan

        if 'Drug' in df.columns:
            # 按 Drug 分组，用组内中位数填补
            df['PDL1_TPS'] = df.groupby('Drug')['PDL1_TPS'] \
                                .transform(lambda x: x.fillna(x.median()))
        
        # 若仍有缺失（某些 Drug 组全缺失）
        df['PDL1_TPS'].fillna(df['PDL1_TPS'].median(), inplace=True)

    # ========= 3. 分类变量 =========
    cat_cols = ['Sex', 'OS_Event', 'PFS_Event', 'Drug', 'Response']
    for col in cat_cols:
        if col in df.columns and df[col].isnull().sum() > 0:
            mode_val = df[col].mode()[0] if not df[col].mode().empty else 0
            df[col].fillna(mode_val, inplace=True)

    # ========= 4. Cohort =========
    if 'Cohort' in df.columns:
        df['Cohort'].fillna('Unknown', inplace=True)

    return df


def handle_outliers(df):
    if 'PDL1_TPS' in df.columns:
        df = df[(df['PDL1_TPS'] >= 0) & (df['PDL1_TPS'] <= 100)]

    if 'Age' in df.columns:
        df = df[(df['Age'] >= 18) & (df['Age'] <= 100)]

    cont_cols = ['NLR', 'Albumin', 'TMB']
    for col in cont_cols:
        if col in df.columns:
            Q1 = df[col].quantile(0.25)
            Q3 = df[col].quantile(0.75)
            IQR = Q3 - Q1
            df[col] = df[col].clip(Q1 - 1.5 * IQR, Q3 + 1.5 * IQR)

    return df


def validate_survival_data(df):
    if 'OS_Event' in df.columns:
        df['OS_Event'] = df['OS_Event'].apply(lambda x: 1 if x == 1 else 0)
    if 'PFS_Event' in df.columns:
        df['PFS_Event'] = df['PFS_Event'].apply(lambda x: 1 if x == 1 else 0)
    return df


def feature_engineering(df):
    if 'NLR' in df.columns and 'Albumin' in df.columns:
        df['NLR_Alb_Score'] = df['NLR'] / df['Albumin']
        df['NLR_Alb_Score'].replace([np.inf, -np.inf], np.nan, inplace=True)
        df['NLR_Alb_Score'].fillna(df['NLR_Alb_Score'].median(), inplace=True)
    return df


def preprocess_tables(tables: Dict[str, Table]) -> Dict[str, Table]:
    print("\n===========================")
    print("Preprocessing data...")
    print("===========================")

    new_tables = {}

    for tbl_name, tbl in tables.items():
        df = tbl.df.copy()
        schema_df = tbl.schema

        for _, row in schema_df.iterrows():
            col = row['column_name']
            dtype = str(row['data_type']).lower()

            if col not in df.columns:
                continue

            if 'datetime' in dtype:
                df[col] = pd.to_datetime(df[col], errors='coerce')
            elif dtype in {'float', 'double', 'decimal'}:
                df[col] = pd.to_numeric(df[col], errors='coerce')
            elif dtype in {'integer', 'int'}:
                df[col] = pd.to_numeric(df[col], errors='coerce', downcast='integer')
            else:
                df[col] = df[col].astype(str)

        missing_value_analysis(df, tbl_name)
        df = fill_missing_values(df)
        df = handle_outliers(df)
        df = validate_survival_data(df)
        df = feature_engineering(df)

        new_tables[tbl_name] = Table(df=df, schema=tbl.schema)

    return new_tables
