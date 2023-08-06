from pydantic import BaseModel, Field


class TextParam(BaseModel):
    """
    文本处理类任务通用参数模型
    """
    # 序列码
    sn: str = Field(description="序列码", default=None)
    # 任务文本
    text: str = Field(description="任务文本")
