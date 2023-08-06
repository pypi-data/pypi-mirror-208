# ez0th - Python Library for Easy Authentication and Authorization

下の方に日本語の説明があります

## Overview
- `ez0th` is a Python library designed to simplify the process of implementing authentication and authorization in your applications. The library follows the Dependency Inversion Principle, making it highly flexible and adaptable to various web frameworks such as Django, Flask, and FastAPI, as well as different types of databases.

## Features
- Simplifies the implementation of authentication and authorization functions such as login.
- Designed following the Dependency Inversion Principle.
- Supports various backends including any type of database by providing a suitable connection function. By default, it uses the json-stock database.
- Allows the use of multiple user IDs and provides efficient user lookup.
- Securely stores passwords using hashing techniques, protecting them even in case of a database breach.
- Generates hard-to-guess internal IDs and salts using cryptographically secure random numbers.
- The library name ez0th is pronounced as "easy auth".

## Usage Example
```python
# Authentication & Authorization Tool [ez0th]
# [Usage Example / Test]

import ez0th

# Default ez0th database [ez0th]
db = ez0th.json_stock("./__ez0th_user_db__/")

# Account registration [ez0th]
success_flag = ez0th.new_account(
    id_dic={"user_id": "WhiteDog", "mail": "example@example.com"},  # ID list (dictionary of all identifiers that can be used as login IDs, such as email addresses)
    password="abc123",  # Password
    info={},  # Other account information
    db=db,  # Database
)

# Result check
print(success_flag)

# Authentication (Login) [ez0th]
success_flag, sess_token = ez0th.login(
    u_id="WhiteDog",  # Login ID (any registered ID is acceptable)
    password="abc123",  # Password
    db=db,  # Database
    timeout=24 * 10  # Timeout duration (in hours; specify inf for infinite duration)
)

# Result check
print(success_flag)
print(sess_token)

# Authorization (Login confirmation) [ez0th]
success_flag, info = ez0th.auth(
    sess_token=sess_token,  # Session token
    db=db  # Database
)

# Result check
print(success_flag)
print(info)

# Check the database
import json_stock as jst
print("db_state:")
print(jst.JsonStock("__ez0th_user_db__"))
```

## Creating Custom Connection Functions
To write a custom connection function, you need to store a dictionary with the keys create, read, update, delete, and contains in the db variable. For the values, you should store functions that have been processed to act as a key-value type database using strings as keys and values. For example, the create function would be used like this: `create(key, value)`. The input and output for the other functions are as follows:

- `value = read(key)`
- `update(key, value)`
- `delete(key)`
- `flag = contains(key)`

Even when using a database like SQL as the backend, you will need to adapt and transform the interface to match the above format to work as a key-value type.

Note that when using the default ez0th.db(), the return value also takes the form described above.

## Precautions
- While this library provides basic authentication and authorization features, developers themselves need to take appropriate measures to ensure the overall security of their applications. For example, consider implementing HTTPS for secure communication and measures against XSS attacks.
- Although password protection uses hashing technology, it does not guarantee sufficient security. Consider implementing regular password changes and strong password policies.


# ez0th - 認証・認可を簡単に実装するPythonライブラリ

## 概要
- `ez0th`は、認証・認可機能を簡単に実装するためのPythonライブラリです。「依存性逆転の原則」に従って設計されているため、DjangoやFlask、FastAPIなどのWebフレームワークや様々なデータベースに柔軟に対応できます。

## 特徴
- ログインなどの認証・認可機能を簡単に記述できます。
- 複数のユーザーIDを使用可能です。
- パスワードはハッシュ技術を用いて暗号化され、安全に保管されます。データベースが流出しても、パスワードはある程度守られます。
- 内部IDやソルトの生成には、推測が困難な「暗号学的乱数」を使用しています。
- ライブラリ名の「ez0th」は、「イージー・オース(easy auth)」と読みます。
- 「依存性逆転の原則」に従って設計されています。
    - そのため、適切な接続関数を用意することで、様々なデータベースをバックエンドとして利用できます。デフォルトでは、「json-stock」データベースを使用します。

## 使い方例
```python
# 認証・認可ツール [ez0th]
# 【動作確認 / 使用例】

import ez0th

# ez0thのデフォルトDB [ez0th]
db = ez0th.json_stock("./__ez0th_user_db__/")

# アカウント登録 [ez0th]
success_flag = ez0th.new_account(
    id_dic={"user_id": "WhiteDog", "mail": "example@example.com"},  # id一覧 (メールアドレス等、ログイン時にidとして用いることのできるすべての識別子の辞書)
    password="abc123",  # パスワード
    info={},  # その他のアカウント情報
    db=db,  # データベース
)

# 結果確認
print(success_flag)

# 認証 (ログイン) [ez0th]
success_flag, sess_token = ez0th.login(
    u_id="WhiteDog",  # ログインid (登録されたいずれのidも可)
    password="abc123",  # パスワード
    db=db,  # データベース
    timeout=24 * 10  # タイムアウト時間 (時間単位; inf指定で無限大)
)

# 結果確認
print(success_flag)
print(sess_token)

# 認可 (ログイン確認) [ez0th]
success_flag, info = ez0th.auth(
    sess_token=sess_token,  # セッショントークン
    db=db  # データベース
)

# 結果確認
print(success_flag)
print(info)

# db確認
import json_stock as jst
print("db_state:")
print(jst.JsonStock("__ez0th_user_db__"))
```

## カスタム接続関数の作成方法
カスタム接続関数を書くには、db変数に、create、read、update、delete、containsの5つのキーを持つ辞書を入れます。値としては、文字列をキーと値としてキー・値型のデータベースとして挙動するようなインターフェースに加工された関数を入れます。例えば、createは、`create(key, value)`のように使用します。その他の関数の入出力は以下の通りです。

- `value = read(key)`
- `update(key, value)`
- `delete(key)`
- `flag = contains(key)`

SQLのようなデータベースをバックエンドとする際も、キー・値型になるようにインターフェースを工夫・変形して上記の形に合わせる必要があります。

なお、デフォルトのez0th.db()を使用した場合でも、返り値は上記の形をしています。

## 注意点
- このライブラリは、認証・認可の基本的な機能を提供しますが、アプリケーション全体のセキュリティに関しては、開発者自身が適切な対策を講じる必要があります。例えば、セキュアな通信を行うためのHTTPSの導入や、XSS対策なども検討してください。
- パスワードの保護は、ハッシュ技術を用いていますが、それでも十分なセキュリティが保証されるわけではありません。定期的なパスワード変更や、強力なパスワードポリシーの導入を検討してください。
