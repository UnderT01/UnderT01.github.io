import os
import random
import uuid

from flask import render_template, Flask, request, redirect, url_for, jsonify
from flask_sqlalchemy import SQLAlchemy
from werkzeug.utils import secure_filename, redirect

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///recipes.db"
db = SQLAlchemy(app)


class Recipe(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(50), nullable=True)
    description = db.Column(db.String(300), nullable=True)
    instructions = db.Column(db.Text(3000), nullable=True)
    category = db.Column(db.String(50), nullable=True)
    image = db.Column(db.String(255), nullable=True)

    def __repr__(self):
        return "<Recipe %r>" % self.title


@app.route("/")
def main():
    return render_template("main.html")


@app.route("/create", methods=["GET", "POST"])
def create():
    if request.method == "POST":
        title = request.form["title"]
        description = request.form["description"]
        instructions = request.form["instructions"]
        category = request.form["category"]

        photo = request.files.get("photo")
        image_filename = None
        if photo and photo.filename != "":
            filename = secure_filename(photo.filename)
            ext = os.path.splitext(filename)[1]
            unique_name = f"{uuid.uuid4().hex}{ext}"
            filepath = os.path.join("static/pictures", unique_name)
            photo.save(filepath)
            image_filename = unique_name

        recipe = Recipe(
            title=title,
            description=description,
            instructions=instructions,
            category=category,
            image=image_filename,
        )
        try:
            db.session.add(recipe)
            db.session.commit()
            return redirect("/")
        except:
            return "Где-то косячнул. Попробуй еще раз)"

    else:
        return render_template("create.html")


@app.route("/all_recipes")
def all_recipes():
    recipes = Recipe.query.order_by(Recipe.title).all()
    return render_template("all_recipes.html", recipes=recipes)


@app.route("/recipe_detail/<int:recipe_id>")
def recipe_detail(recipe_id):
    recipe = Recipe.query.get_or_404(recipe_id)
    return render_template("recipe_detail.html", recipe=recipe)


@app.route("/recipe/<int:recipe_id>/delete")
def recipe_delete(recipe_id):
    recipe = Recipe.query.get_or_404(recipe_id)

    try:
        db.session.delete(recipe)
        db.session.commit()
        return redirect("/all_recipes")
    except:
        return "Нельзя удалить то чего нет"


@app.route("/recipe/<int:recipe_id>/update", methods=["GET", "POST"])
def recipe_update(recipe_id):
    recipe = Recipe.query.get_or_404(recipe_id)
    if request.method == "POST":
        recipe.title = request.form["title"]
        recipe.description = request.form["description"]
        recipe.instructions = request.form["instructions"]
        recipe.category = request.form["category"]

        photo = request.files.get("photo")
        if photo and photo.filename != "":
            if recipe.image:
                old_path = os.path.join("static/pictures", recipe.image)
                if os.path.exists(old_path):
                    os.remove(old_path)
            filename = secure_filename(photo.filename)
            ext = os.path.splitext(filename)[1]
            unique_name = f"{uuid.uuid4().hex}{ext}"
            filepath = os.path.join("static/pictures", unique_name)
            photo.save(filepath)
            recipe.image = unique_name

        try:
            db.session.commit()
            return redirect(url_for("recipe_detail", recipe_id=recipe.id))
        except:
            return "Шото не так, но я не виноват. Попробуй еще раз)"

    else:
        return render_template("recipe_update.html", recipe=recipe)


@app.route("/hot-recipes")
def hot_recipes():
    recipes = Recipe.query.filter_by(category="горячее").all()
    return render_template("hot_recipes.html", recipes=recipes)


@app.route("/cold-recipes")
def cold_recipes():
    recipes = Recipe.query.filter_by(category="холодное").all()
    return render_template("cold_recipes.html", recipes=recipes)


@app.route("/salad-recipes")
def salad_recipes():
    recipes = Recipe.query.filter_by(category="салат").all()
    return render_template("salad_recipes.html", recipes=recipes)


@app.route("/snacks-recipes")
def snacks_recipes():
    recipes = Recipe.query.filter_by(category="закуска").all()
    return render_template("snacks_recipes.html", recipes=recipes)


@app.route("/soups-recipes")
def soups_recipes():
    recipes = Recipe.query.filter_by(category="супы").all()
    return render_template("soups_recipes.html", recipes=recipes)


@app.route("/delivery-recipes")
def delivery_recipes():
    recipes = Recipe.query.filter_by(category="доставка").all()
    return render_template("delivery_recipes.html", recipes=recipes)


@app.route("/search")
def search():
    query = request.args.get("q", "")
    if query:
        results = Recipe.query.filter(
            Recipe.title.ilike(f"%{query}%") | Recipe.description.ilike(f"%{query}%")
        ).all()
    else:
        results = []
    return render_template("search_results.html", recipes=results, query=query)


@app.route("/random_recipe")
def random_recipe():
    recipes = Recipe.query.all()
    if not recipes:
        return jsonify({"error": "Нет рецептов"}), 200
    r = random.choice(recipes)
    image_url = (
        url_for("static", filename=f"pictures/{r.image}")
        if r.image
        else url_for("static", filename="pictures/default.jpg")
    )
    return jsonify(
        {
            "id": r.id,
            "title": r.title,
            "description": r.description,
            "category": r.category,
            "image": image_url,
        }
    )


@app.route("/random_recipe_by_category")
def random_recipe_by_category():
    cat = request.args.get("category", "")
    if not cat:
        return jsonify({"error": "Не указана категория"}), 400
    recipes = Recipe.query.filter_by(category=cat).all()
    if not recipes:
        return jsonify({"error": f"Нет рецептов в категории {cat}"}), 200
    r = random.choice(recipes)
    image_url = (
        url_for("static", filename=f"pictures/{r.image}")
        if r.image
        else url_for("static", filename="pictures/default.jpg")
    )
    return jsonify(
        {
            "id": r.id,
            "title": r.title,
            "description": r.description,
            "category": r.category,
            "image": image_url,
        }
    )


if __name__ == "__main__":
    app.run(debug=True)
