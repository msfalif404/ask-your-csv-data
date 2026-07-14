import functools
from pathlib import Path

class PromptManager:
    """
    Manager class to load and expose prompt templates as properties.
    """
    def __init__(self):
        # Menggunakan pathlib untuk penanganan path yang lebih bersih dan modern
        self.templates_dir = Path(__file__).parent / "templates"
        
    @functools.lru_cache(maxsize=10)
    def _read_template(self, filename: str) -> str:
        filepath = self.templates_dir / filename
        if not filepath.exists():
            raise FileNotFoundError(f"Prompt template '{filename}' not found in {self.templates_dir}")
            
        return filepath.read_text(encoding='utf-8')

    @property
    def router_prompt(self) -> str:
        """Prompt untuk agen Router yang menentukan intent (question vs visualization)."""
        return self._read_template("router_prompt.md")

    @property
    def answer_planner_prompt(self) -> str:
        """Prompt untuk agen perencana pengambil jawaban numerik/insight."""
        return self._read_template("answer_planner_prompt.md")
        
    @property
    def visualization_planner_prompt(self) -> str:
        """Prompt untuk agen perencana grafik dan visualisasi data."""
        return self._read_template("visualization_planner_prompt.md")

    @property
    def schema_selector_prompt(self) -> str:
        """Prompt untuk agen Dynamic Column Selector."""
        return self._read_template("schema_selector_prompt.md")

    @property
    def analyzer_prompt(self) -> str:
        """Prompt untuk agen Analis Bisnis."""
        return self._read_template("analyzer_prompt.md")
