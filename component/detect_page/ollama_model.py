import asyncio
import pathlib

from qfluentwidgets import HeaderCardWidget, PushButton, FluentIcon
from ollama import AsyncClient
from custom_widget.message_box import TipMessageBox
from custom_widget.ollama_output_text import OllamaOutputText
import qasync

from custom_widget.process_message import ProcessMessage
from shared_data import shared_data
from utils.utils import is_img


class OllamaModelWidget(HeaderCardWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setTitle("质检报告")
        self.headerLabel.setObjectName("ollama_model_header")
        self.setBorderRadius(8)

        self.report_button = PushButton(FluentIcon.ROBOT, "生成报告")
        self.headerLayout.addWidget(self.report_button)

        # 输出框
        self.output_display = OllamaOutputText()

        # ollama设置
        self.ollama_client = AsyncClient()
        self.is_running = False

        # 要把组件和布局添加到HeaderCardWidget的viewLayout才会显示
        self.viewLayout.addWidget(self.output_display)

        # 应用QSS
        with open("resource/qss/ollama_model.qss", encoding='utf-8') as f:
            self.setStyleSheet(f.read())

    @qasync.asyncSlot()
    async def run_ollama_model(self, file_path):
        if not shared_data.save_dir:
            w = TipMessageBox("请先处理图片", '左侧"检测结果"面板，点击"开始处理"按钮进行处理', self.window())
            w.exec()
            return

        if self.is_running and not is_img(file_path):
            return

        predicted_img_path = pathlib.Path(shared_data.save_dir) / pathlib.Path(file_path).name
        if predicted_img_path.exists():
            self.is_running = True
            self.report_button.setEnabled(False)
            self.output_display.clear()

            # 弹出"正在处理"消息框
            self.process_message = ProcessMessage('正在生成中', '请耐心等待哦~~', self.parent())
            self.process_message.show()
            prompt = ('''
            你是一位拥有20年以上行业经验的资深缺陷质检专家。请你仔细分析我上传的这张缺陷图片，根据图片中已标注的缺陷类型和位置，生成一份专业、规范的缺陷质检报告。
            要求：
            1. 报告语言简洁专业，结构清晰，逻辑严谨，使用行业标准术语，使用中文纯文本回复，不要使用markdown等富文本格式
            2. 准确描述每个标注缺陷的视觉特征、大致位置和明显尺寸，标签旁边的数值为置信度
            3. 对每个缺陷进行严重程度分级（致命/严重/一般/轻微）
            4. 给出明确的质量判定结果和初步处理建议，不需要写生成时间
            ''')

            await self.chat(
                prompt=prompt,
                img_path=predicted_img_path,
                model="qwen3.5:2b"
            )

    async def chat(self, prompt, img_path, model):
        message = {'role': 'user', 'content': prompt, 'images':[f'{img_path}']}
        try:
            async for part in await self.ollama_client.chat(
                    model=model,
                    messages=[message],
                    stream=True
            ):
                content = part['message']['content']
                self.output_display.append_text(content)
                await asyncio.sleep(0)

        except Exception as e:
            self.output_display.append_text(f"\n错误: {str(e)}")
        finally:
            self.is_running = False
            self.report_button.setEnabled(True)
            self.process_message.finished("生成完毕", "")  # 结束"正在处理"消息框