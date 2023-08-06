# 認証・認可ツール [ez0th]

import sys
import time
import slim_id
import hashlib
from sout import sout
from relpath import add_import_path

# 引数インジェクションチェック (セキュリティー対策; ptnを満たす文字列かどうかをチェック)
def check_injection(
	arg_str,	# チェック対象の文字列
	ptn = None	# 満たすべき文字列パターン (None指定でチェックなし)
):
	# 例外オブジェクト
	err_obj = Exception("[ez0th error] Injection detected.")
	# 型の判定
	if type(arg_str) != type(""): raise err_obj
	# 文字列の出だしの判定
	if ptn is None: return "OK"
	if arg_str.startswith(ptn) is False: raise err_obj
	return "OK"

# ez0thのデフォルトDB [ez0th]
def json_stock(
	db_dir = "./__ez0th_user_db__/",	# DBのディレクトリ指定
):
	import json_stock as jst
	# DBを開く (存在しない場合はディレクトリが自動的に作成される)
	jst_db = jst.JsonStock(db_dir)
	# テーブルの作成
	if "__ez0th_general_table__" not in jst_db:
		jst_db["__ez0th_general_table__"] = {}
	table = jst_db["__ez0th_general_table__"]
	# CRUD機能の定義
	def create_update_func(k, v): table[k] = v	# 新データ作成・データ置き換え関数
	def read_func(k): return table[k]	# データ読み出し関数
	def delete_func(k): del table[k]	# データ削除関数
	def contains_func(k): return (k in table)	# データ存在確認関数
	# 各機能をまとめて返却
	return {
		"create": create_update_func,
		"read": read_func,
		"update": create_update_func,
		"delete": delete_func,
		"contains": contains_func,
	}

# アカウント存在確認 [ez0th]
def is_exists(
	u_id,	# ログインid (登録されたいずれのidも可)
	db = "auto",	# データベース
):
	if db == "auto": db = json_stock("./__ez0th_user_db__/")
	# 引数インジェクションチェック (セキュリティー対策; ptnを満たす文字列かどうかをチェック)
	check_injection(u_id)
	return db["contains"]("id_"+u_id)

# パスワードのハッシュ化 (パスワードを安全に保管するため)
def gen_pw_hash(password, pw_salt = "random"):
	# saltの生成
	if pw_salt == "random": pw_salt = gen_rand_token()	# 十分長のランダムなトークンを生成 (暗号学的乱数)
	# hashの生成
	salted_password = pw_salt + password	# saltとパスワードを結合
	pw_hash = hashlib.sha256(salted_password.encode()).hexdigest()
	return pw_salt, pw_hash

# 内部ユーザーidの生成 (システム内で利用するため; "inner_id_"で開始するID)
def gen_inner_id(db):
	def judge_exists(core_id):
		return db["contains"]("inner_id_"+core_id)
	inner_id = "inner_id_" + slim_id.gen(judge_exists)
	return inner_id

# アカウント登録 [ez0th]
def new_account(
	id_dic,	# id一覧 (メールアドレス等、ログイン時にidとして用いることのできるすべての識別子の辞書)
	password,	# パスワード
	info = {},	# その他のアカウント情報
	db = "auto",	# データベース
):
	if db == "auto": db = json_stock("./__ez0th_user_db__/")
	# 引数インジェクションチェック (セキュリティー対策; ptnを満たす文字列かどうかをチェック)
	for id_type in id_dic: check_injection(id_dic[id_type])
	check_injection(password)
	# アカウント存在確認
	for id_type in id_dic:
		if is_exists(id_dic[id_type], db) is True: return False
	# パスワードのハッシュ化 (パスワードを安全に保管するため)
	pw_salt, pw_hash = gen_pw_hash(password)
	# 内部ユーザーidの生成 (システム内で利用するため; "inner_id_"で開始するID)
	inner_id = gen_inner_id(db)
	# DBへの登録
	new_value = {"inner_id": inner_id, "id_dic": id_dic, "pw_salt": pw_salt, "pw_hash": pw_hash, "info": info}
	db["create"](inner_id, new_value)
	for id_type in id_dic: db["create"]("id_"+id_dic[id_type], inner_id)
	return True

# 十分長のランダムなトークンを生成 (暗号学的乱数)
def gen_rand_token():
	# slim-idの内部は暗号学的乱数なので推測困難
	return slim_id.gen(
		lambda e: False,	# 母集団が十分広いので復元抽出とする
		length = 16
	)

# セッショントークンの発行
def gen_sess_token(inner_id, timeout, db):
	sess_token = "sess_token_" + gen_rand_token()	# 十分長のランダムなトークンを生成 (暗号学的乱数)
	login_time = time.time()	# unix-time
	expire_time = (
		"inf"
		if timeout == "inf"
		else login_time + timeout * 60 ** 2)
	db["create"](sess_token, {
		"inner_id": inner_id,
		"sess_token": sess_token,
		"login_time": login_time,
		"duration_hours": timeout,
		"expire_time": expire_time,
	})
	return sess_token

# 認証 (ログイン) [ez0th]
def login(
	u_id,	# ログインid (登録されたいずれのidも可)
	password,	# パスワード
	timeout = "inf",	# タイムアウト時間 (時間単位; inf指定で無限大)
	db = "auto"	# データベース
):
	if db == "auto": db = json_stock("./__ez0th_user_db__/")
	# 引数インジェクションチェック (セキュリティー対策; ptnを満たす文字列かどうかをチェック)
	check_injection(u_id)
	check_injection(password)
	# アカウント存在確認 [ez0th]
	if is_exists(u_id, db) is False: return False, None	# success_flag, sess_token
	# パスワード正当性確認
	inner_id = db["read"]("id_" + u_id)
	account_data = db["read"](inner_id)
	_, temp_hash = gen_pw_hash(password, account_data["pw_salt"])	# パスワードのハッシュ化 (パスワードを安全に保管するため)
	if temp_hash != account_data["pw_hash"]: return False, None	# success_flag, sess_token
	# セッショントークンの発行
	sess_token = gen_sess_token(inner_id, timeout, db)
	return True, sess_token

# 認可 (ログイン確認) [ez0th]
def auth(
	sess_token,	# セッショントークン
	db = "auto"	# データベース
):
	if db == "auto": db = json_stock("./__ez0th_user_db__/")
	# 引数インジェクションチェック (セキュリティー対策; ptnを満たす文字列かどうかをチェック)
	check_injection(sess_token, ptn = "sess_token_")
	# セッショントークンの実在性確認
	if db["contains"](sess_token) is False: return False, "invalid_sess_token"
	# セッション情報の取得
	sess_info = db["read"](sess_token)
	# セッションの有効期限の確認
	if sess_info["expire_time"] != "inf":
		if time.time() > sess_info["expire_time"]: return False, "the_session_has_expired"
	# 有効なセッショントークン
	return True, sess_info
