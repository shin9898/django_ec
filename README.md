# Django EC サイト

このリポジトリは、Django を用いたシンプルな EC サイト構築プロジェクトです。商品一覧表示、カート機能、注文処理、プロモーションコードの適用などの基本的な EC 機能を備えています。

---

## 🚀 本番環境URL

- https://infinite-everglades-35887-c61444eb0da9.herokuapp.com/

---

## 🎯 主な機能

- 商品一覧・詳細ページ（Bootstrap テンプレート使用）
- 商品管理機能（Basic認証付き）
- カート機能（セッションベースでユーザーごとに独立）
- チェックアウト（フォーム送信→DB登録）
- プロモーションコード適用（1回限り、割引額付き）
- 購入明細保存・メール送信

---

## 🔐 認証情報

- 商品管理ページおよび注文明細画面には Basic 認証が必要です。
- 認証情報は `.env` に設定されています（本番環境では非公開環境変数として管理）。

---

## 🧾 プロモーションコード機能

- 7桁の英数字からなるコードを管理画面またはコマンドから発行可能
- 1回限り有効な割引（100〜1000円）
- 以下のコマンドで自動生成できます：

```
python manage.py promotion_code_generate
```

---

## 📦 プロジェクト構成

```
django_ec/
├── config/
├── cart/              # カート機能
├── item/              # 商品表示・管理
├── manage/            # 管理用ビュー（Basic認証付き）
├── order/             # 注文・決済
├── promotion_code/    # プロモーションコード管理
├── templates/         # HTMLテンプレート（Bootstrap）
├── static/            # 静的ファイル（CSS/JS/画像）
├── Dockerfile
├── docker-compose.yml
├── requirements.txt
└── manage.py
```

---

## 📨 メール送信

注文完了時にユーザー宛へ購入明細を送信。
※開発環境ではコンソール出力、Herokuの本番環境ではBrevoの外部サービス連携を使用

---

## 📎 使用技術

- Python 3.12
- Django 4.2.23
- PostgreSQL 17.5
- Bootstrap
- 開発環境：Docker
- 本番環境：Heroku
- 画像保存：Cloudinary
- メール送信：Brevo（SMTP API 経由）


---

## 📄 ライセンス

このリポジトリは MIT ライセンスのもとで公開されています。
