from flask import Flask, render_template, redirect, url_for, request
from flask_bootstrap import Bootstrap5
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy import Integer, String, Float
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired
import requests
api_key='your key'
url = "https://api.themoviedb.org/3/search/movie"

'''
Red underlines? Install the required packages first: 
Open the Terminal in PyCharm (bottom left). 

On Windows type:
python -m pip install -r requirements.txt

On MacOS type:
pip3 install -r requirements.txt

This will install the packages from requirements.txt for this project.
'''
class Base(DeclarativeBase):
    pass

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your keyf'
Bootstrap5(app)

# CREATE DB
db=SQLAlchemy(model_class=Base)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///movie-collection.db"
db.init_app(app)
class movies(db.Model):
    id:Mapped[int]=mapped_column(Integer,primary_key=True)
    title:Mapped[str]=mapped_column(String,unique=True)
    year:Mapped[int]=mapped_column(Integer)
    description:Mapped[str]=mapped_column(String)
    rating:Mapped[float]=mapped_column(Float,nullable=True)
    ranking:Mapped[int]=mapped_column(Integer,nullable=True)
    review:Mapped[str]=mapped_column(String,nullable=True)
    img_url:Mapped[str]=mapped_column(String)
with app.app_context():
    db.create_all()
    new_movie = movies(
        title="Phone Booth",
        year=2002,
        description="Publicist Stuart Shepard finds himself trapped in a phone booth, pinned down by an extortionist's sniper rifle. Unable to leave or receive outside help, Stuart's negotiation with the caller leads to a jaw-dropping climax.",
        rating=7.3,
        ranking=10,
        review="My favourite character was the caller.",
        img_url="https://image.tmdb.org/t/p/w500/tjrX2oWRCM3Tvarz38zlZM7Uc10.jpg"
    )
    second_movie = movies(
        title="Avatar The Way of Water",
        year=2022,
        description="Set more than a decade after the events of the first film, learn the story of the Sully family (Jake, Neytiri, and their kids), the trouble that follows them, the lengths they go to keep each other safe, the battles they fight to stay alive, and the tragedies they endure.",
        rating=7.3,
        ranking=9,
        review="I liked the water.",
        img_url="https://image.tmdb.org/t/p/w500/t6HIqrRAclMCA60NsSmeqe9RmNV.jpg"
    )
    # db.session.add(second_movie)
    # db.session.commit()

# CREATE TABLE
class RateMovieForm(FlaskForm):
    rating = StringField("Your Rating Out of 10 e.g. 7.5")
    review = StringField("Your Review")
    submit = SubmitField("Done")
class AddMovieForm(FlaskForm):
    movie_title=StringField("Movie-title")
    add_movie=SubmitField("Add Movie")
@app.route("/")
def home():
 with app.app_context():
    first=db.session.execute(db.select(movies).order_by(movies.rating)).scalars().all()
    print(first)
    for i in range(len(first)):
        first[i].ranking=len(first)-i
    return render_template("index.html",first=first)
@app.route('/edit',methods=['GET','POST'])
def edit():
    form=RateMovieForm()
    if form.validate_on_submit():
        id=request.args.get('id')
        edited_review=db.get_or_404(movies,id)
        edited_review.review=request.form['review']
        edited_review.rating=request.form['rating']
        db.session.commit()
        return redirect(url_for('home'))
    return render_template('edit.html',form=form)
@app.route('/add',methods=['GET','POST'])
def add():
    form=AddMovieForm()
    if form.validate_on_submit():
        movie_title=request.form['movie_title']
        response = requests.get(url,params={'query':movie_title,'api_key':api_key})
        response=response.json()
        return render_template('select.html',options=response['results'])
    return render_template('add.html',form=form)
@app.route('/details')
def details():
    movie_id=request.args.get('id')
    url=f'https://api.themoviedb.org/3/movie/{movie_id}'
    response = requests.get(url, params={'api_key': api_key})
    response = response.json()
    print(response)
    date_string =response['release_date']
    year = date_string[:4]
    new_movie = movies(
        title=response['original_title'],
        year=int(year),
        description=response['overview'],
        img_url=f"https://image.tmdb.org/t/p/original{response['poster_path']}",
    )
    db.session.add(new_movie)
    db.session.commit()

    return redirect(url_for('edit',id=new_movie.id))

@app.route('/delete')
def delete():
    id = request.args.get('id')
    movie = db.get_or_404(movies, id)
    db.session.delete(movie)
    db.session.commit()
    return redirect(url_for('home'))




if __name__ == '__main__':
    app.run(debug=True)
