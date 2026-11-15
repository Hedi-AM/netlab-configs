import json
import ubus

sid = ubus.login()
print("ubus_rpc_session:", sid)
board = ubus.call(ubus.HOST, sid, "system", "board")
print("Session reused for system.board:")
print(json.dumps(board, indent=2))
