# 認証・認可ツール [ez0th]
# 【動作確認 / 使用例】

import sys
from sout import sout
from ezpip import load_develop
# 認証・認可ツール [ez0th]
ez0th = load_develop("ez0th", "../", develop_flag = True)

# ez0thのデフォルトDB [ez0th]
db = ez0th.json_stock("./__ez0th_user_db__/")

# アカウント登録 [ez0th]
success_flag = ez0th.new_account(
	id_dic = {"user_id": "WhiteDog"},	# id一覧 (メールアドレス等、ログイン時にidとして用いることのできるすべての識別子の辞書)
	password = "abc123",	# パスワード
	info = {},	# その他のアカウント情報
	db = db,	# データベース
)
# 結果確認
print(success_flag)

# 認証 (ログイン) [ez0th]
success_flag, sess_token = ez0th.login(
	u_id = "WhiteDog",	# ログインid (登録されたいずれのidも可)
	password = "abc123",	# パスワード
	db = db,	# データベース
	timeout = 24 * 10	# タイムアウト時間 (時間単位; inf指定で無限大)
)
# 結果確認
print(success_flag)
print(sess_token)

# 認可 (ログイン確認) [ez0th]
success_flag, info = ez0th.auth(
	sess_token = sess_token,	# セッショントークン
	db = "auto"	# データベース
)
# 結果確認
print(success_flag)
print(info)

# db確認
import json_stock as jst
print("db_state:")
print(jst.JsonStock("__ez0th_user_db__"))
sys.exit()
