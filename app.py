from flask import Flask, render_template, request, redirect, url_for, send_from_directory
from flask_sqlalchemy import SQLAlchemy
from werkzeug.utils import secure_filename
import os
from config import Config

app = Flask(__name__)
app.config.from_object(Config)

db = SQLAlchemy(app)

# -------------------------
# 商品資料表
# -------------------------
class Item(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.String(200))
    store = db.Column(db.String(100))
    price = db.Column(db.String(50))
    category = db.Column(db.String(100))
    image = db.Column(db.String(300))

# -------------------------
# 訂單資料表
# -------------------------
class Order(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    item_id = db.Column(db.Integer)
    buyer_location = db.Column(db.String(200))
    buyer_phone = db.Column(db.String(50))
    buyer_email = db.Column(db.String(100))

# -------------------------
# 首頁（含搜尋功能）
# -------------------------
@app.route("/", methods=["GET", "POST"])
def index():
    q = request.args.get("q", "")
    category_filter = request.args.get("category", "")

    query = Item.query

    if q:
        query = query.filter(Item.content.contains(q))

    if category_filter:
        query = query.filter_by(category=category_filter)

    items = query.all()

    categories = [
        "車輛", "房屋租賃", "免費商品", "分類廣告", "嗜好", "園藝和戶外用品",
        "娛樂", "家庭", "寵物用品", "居家用品", "居家裝潢用品", "房屋銷售",
        "服飾", "樂器", "玩具和遊戲", "辦公用品", "運動用品", "電子產品",
        "商品買賣社團"
    ]

    return render_template("index.html", items=items, categories=categories)

# -------------------------
# 新增商品
# -------------------------
@app.route("/add", methods=["GET", "POST"])
def add_item():
    categories = [
        "車輛", "房屋租賃", "免費商品", "分類廣告", "嗜好", "園藝和戶外用品",
        "娛樂", "家庭", "寵物用品", "居家用品", "居家裝潢用品", "房屋銷售",
        "服飾", "樂器", "玩具和遊戲", "辦公用品", "運動用品", "電子產品",
        "商品買賣社團"
    ]

    if request.method == "POST":
        content = request.form["content"]
        store = request.form["store"]
        price = request.form["price"]
        category = request.form["category"]

        image_file = request.files["image"]
        filename = secure_filename(image_file.filename)
        image_path = os.path.join(app.config["UPLOAD_FOLDER"], filename)
        image_file.save(image_path)

        item = Item(
            content=content,
            store=store,
            price=price,
            category=category,
            image=filename
        )
        db.session.add(item)
        db.session.commit()

        return redirect("/")

    return render_template("add_item.html", categories=categories)

# -------------------------
# 商品詳細 + 購買頁面
# -------------------------
@app.route("/item/<int:item_id>")
def item_detail(item_id):
    item = Item.query.get_or_404(item_id)
    return render_template("item_detail.html", item=item)

# -------------------------
# 下單
# -------------------------
@app.route("/buy/<int:item_id>", methods=["POST"])
def buy_item(item_id):
    location = request.form["location"]
    phone = request.form["phone"]
    email = request.form["email"]

    order = Order(
        item_id=item_id,
        buyer_location=location,
        buyer_phone=phone,
        buyer_email=email
    )
    db.session.add(order)
    db.session.commit()

    return render_template("order_success.html")

# -------------------------
# 刪除商品
# -------------------------
@app.route("/delete/<int:item_id>")
def delete_item(item_id):
    item = Item.query.get_or_404(item_id)
    db.session.delete(item)
    db.session.commit()
    return redirect("/")

# -------------------------
# 圖片路徑
# -------------------------
@app.route("/uploads/<filename>")
def uploaded_file(filename):
    return send_from_directory(app.config["UPLOAD_FOLDER"], filename)

# -------------------------
# 建立資料表
# -------------------------
if __name__ == "__main__":
    if not os.path.exists(Config.UPLOAD_FOLDER):
        os.makedirs(Config.UPLOAD_FOLDER)
    
    # ✅ 修正：在應用程式上下文中建立資料表
    with app.app_context():
        db.create_all()
    
    app.run(debug=True)
