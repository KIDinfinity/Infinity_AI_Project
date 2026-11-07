# lessons_learned/ 目录说明

从复盘自动提炼的结构化教训（`LessonLearned`），单一 JSONL 文件追加写入，由 `knowledge.py::append_lesson_from_review` 在 weekly 复盘后调用生成。`status=deprecated` 的条目不会被 `query_lessons` 返回。格式见 [../../../design/03_data_model.md](../../../design/03_data_model.md) 第 6.2 节。
