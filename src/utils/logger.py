import logging

# 로깅 설정
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO
)

# 로거 생성
logger = logging.getLogger("asynchronous-message-queue")