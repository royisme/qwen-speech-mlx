.PHONY: start stop restart status logs clean install sync \
       start-tts stop-tts restart-tts status-tts logs-tts \
       start-asr stop-asr restart-asr status-asr logs-asr \
       start-all stop-all restart-all status-all test-tts test-asr

# TTS Service (default, port 9955)
start: start-tts
stop: stop-tts
restart: restart-tts
status: status-tts
logs: logs-tts

start-tts:
	@./launch.sh start tts

stop-tts:
	@./launch.sh stop tts

restart-tts:
	@./launch.sh restart tts

status-tts:
	@./launch.sh status tts

logs-tts:
	@tail -f service_tts.log

# ASR Service (port 9956)
start-asr:
	@./launch.sh start asr

stop-asr:
	@./launch.sh stop asr

restart-asr:
	@./launch.sh restart asr

status-asr:
	@./launch.sh status asr

logs-asr:
	@tail -f service_asr.log

# Both services
start-all: start-tts start-asr
stop-all: stop-tts stop-asr
restart-all: stop-all start-all
status-all: status-tts status-asr

# Tests
test-tts:
	@uv run examples/test_tts.py

test-asr:
	@uv run examples/test_asr.py

# Dependencies
install:
	@uv sync

sync:
	@uv sync

# Cleanup
clean:
	@rm -f service_tts.pid service_tts.log service_asr.pid service_asr.log
