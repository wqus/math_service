import sys
import asyncio
from pathlib import Path

# Добавляем папку bot в sys.path
bot_path = str(Path(__file__).parent / "bot")
sys.path.insert(0, bot_path)

from main import main

if __name__ == "__main__":
    asyncio.run(main())