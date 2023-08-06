import pandas as pd
import jieba
from collections import defaultdict


def read_csv(path) -> pd.DataFrame:
    return pd.read_csv(path, encoding='gbk', skiprows=5)


class KeywordSummary:
    """针对关键词进行分词汇总,会用到jieba分词"""

    def __init__(self, dataframe, custom_words=None, filter_words=None):
        self.df = dataframe
        self.custom_words = custom_words or []
        self.filter_words = filter_words or []

        for word in self.custom_words:
            jieba.add_word(word)

    def _split_keywords(self, text):
        return [word for word in jieba.cut(text) if word not in self.filter_words]

    def summarize(self, target_column, summary_columns):
        """
        :param target_column: 目标名,比如搜索词汇总一般就是"搜索词"
        :param summary_columns: 需要汇总的列名
        :return: 汇总后的DataFrame

        # 使用示例
        from tybase.baidu.kw_tool import KeywordSummary
        custom_words = ["手机版","写作猫","国内版","中国版","生成器","创作猫"]   #定义不分词列表
        filter_words = [" ","的"]  # 定义过滤词
        ks = KeywordSummary(df, custom_words, filter_words)
        # 传入需要计算的字段
        summary_df = ks.summarize("搜索词", ["展现", "点击", "消费", "激活数", "注册数", "付费金额"])
        # 返回
        ```txt
        关键词	频次	展现	点击	消费	激活数	注册数	付费金额
    0	手机版	223.0	40223.0	8912.0	11858.01	2867.0	2385.0	12712.0
    1	下载	1362.0	88378.0	20140.0	24303.06	6330.0	5162.0	25668.0
        ```
        """
        self.df["分词"] = self.df[target_column].apply(self._split_keywords)

        summary_data = defaultdict(lambda: defaultdict(float))

        for _, row in self.df.iterrows():
            for word in row["分词"]:
                summary_data[word]["频次"] += 1
                for col in summary_columns:
                    summary_data[word][col] += row[col]

        summary_df = pd.DataFrame.from_dict(summary_data, orient='index')
        summary_df.reset_index(level=0, inplace=True)
        summary_df.rename(columns={'index': '关键词'}, inplace=True)

        return summary_df


class KeywordAggregator:
    """对竞价的关键词,根据条件过滤包含的关键词,分组汇总好对应的数据"""
    def __init__(self, dataframe):
        self.df = dataframe

    def aggregate(self, keyword_dict, summary_columns, roi_formula=None) -> pd.DataFrame:
        """

        :param keyword_dict: 关键词分组字典,比如 {"chatgpt": "chat|gpt", "作文": "作文"}
        :param summary_columns: 需要汇总的列名,比如 ["展现", "点击", "消费", "激活数", "注册数", "付费金额"]
        :param roi_formula: ROI计算公式,比如 "付费金额 / 消费"
        :return: 汇总后的DataFrame

        # 使用示例
        from tybase.baidu.kw_tool import KeywordSummary
        # 创建 KeywordAggregator 实例
        ka = KeywordAggregator(df)


        # 传入分类规则,以及ROI的计算公式

        keyword_dict = {"chatgpt": "chat|gpt",
                        "作文": "作文",
                       }
        summary_columns = ["展现", "点击", "消费", "激活数", "注册数", "付费金额"]
        roi_formula = "付费金额 / 消费"
        aggregated_df = ka.aggregate(keyword_dict, summary_columns, roi_formula)

        """

        result = []
        for keyword_category, keywords in keyword_dict.items():
            filtered_df = self.df[self.df["搜索词"].str.contains(keywords, regex=True)]
            aggregated_data = {col: filtered_df[col].sum() for col in summary_columns}

            # 计算 ROI
            if roi_formula:
                aggregated_data["ROI"] = eval(roi_formula, {}, aggregated_data)

            aggregated_data["关键词分类"] = keyword_category
            result.append(aggregated_data)

        aggregated_df = pd.DataFrame(result)

        # 将 "关键词分类" 列移动到第一个位置
        if roi_formula:
            column_order = ["关键词分类"] + summary_columns + ["ROI"]
        else:
            column_order = ["关键词分类"] + summary_columns
        aggregated_df = aggregated_df[column_order]

        return aggregated_df


if __name__ == '__main__':
    pass
