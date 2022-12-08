from flask import Flask, request, redirect, render_template, url_for
from pymongo import MongoClient
from bson.objectid import ObjectId
import json

############################################################
# SETUP
############################################################

app = Flask(__name__)

mongo = MongoClient('localhost', 27017)
db = mongo.plants_db
plants = db.plants
harvests = db.harvests

############################################################
# ROUTES
############################################################

@app.route('/')
def plants_list():
    """
    Display the plants list page.
    """
    
    plants_data = plants.find()
    context = {
        'plants': plants_data,
    }

    return render_template('plants_list.html', **context)

@app.route('/about')
def about():
    """
    Display the about page.
    """
    return render_template('about.html')

@app.route('/create', methods=['GET', 'POST'])
def create():
    """
    Display the plant creation page & process data from the creation form.
    """
    if request.method == 'POST':

        new_plant = {
            'name': request.form['plant_name'],
            'variety': request.form['variety'],
            'photo_url': request.form['photo'],
            'date_planted': request.form['date_planted']
        }

        new_plant_id = plants.insert_one(new_plant).inserted_id # captures response to get inserted objectId

        return redirect(url_for('detail', plant_id=new_plant_id))

    else:
        return render_template('create.html')

@app.route('/plant/<plant_id>')
def detail(plant_id):
    """
    Display the plant detail page & process data from the harvest form.
    """

    plant_to_show = plants.find_one({'_id': ObjectId(plant_id)})
    find_all_harvests = harvests.find()

    context = {
        'plant' : plant_to_show,
        'harvests': find_all_harvests
    }
    return render_template('detail.html', **context)

@app.route('/harvest/<plant_id>', methods=['POST'])
def harvest(plant_id):
    """
    Accepts a POST request with data for 1 harvest and inserts into database.
    """

    new_harvest = {
        'quantity': request.form['harvested_amount'],
        'date': request.form['date_harvested'],
        'plant_id': plant_id
    }

    harvests.insert_one(new_harvest)

    return redirect(url_for('detail', plant_id=plant_id))

@app.route('/edit/<plant_id>', methods=['GET', 'POST'])
def edit(plant_id):
    """
    Shows the edit page and accepts a POST request with edited data.
    """
    if request.method == 'POST':
        new_plant_details = {
            'name': request.form['plant_name'],
            'variety': request.form['variety'],
            'photo_url': request.form['photo'],
            'date_planted': request.form['date_planted']
        }
        
        plants.update_one({"_id": ObjectId(plant_id)}, {'$set':new_plant_details})
        
        return redirect(url_for('detail', plant_id=plant_id))

    else:
        plant_to_show = plants.find_one({"_id": ObjectId(plant_id)})

        context = {
            'plant': plant_to_show
        }

        return render_template('edit.html', **context)

@app.route('/delete/<plant_id>', methods=['POST'])
def delete(plant_id):
    """
    Accepts a POST request to delete an item and any associated harvests from the database.
    """
    plants.delete_one({"_id": ObjectId(plant_id)})
    harvests.delete_many({"_id": ObjectId(plant_id)})
    return redirect(url_for('plants_list'))

if __name__ == '__main__':
    app.run(debug=True, port=3000)

