from fastapi import FastAPI,Path,HTTPException,Query
import json
app = FastAPI()

def load_data():
    with open('patients.json','r') as f:
        data = json.load(f)
    return data
@app.get('/')

def hello():
    return {'messsage' : ' Patients Management System Api'}

@app.get('/about')
def about():
    return {'Message':'A Fully functional Api to manage your patients records'}

@app.get('/view')
def view():
    data = load_data()
    return data

@app.get('/patients/{patients_id}')

def view_patient(patients_id:str = Path(...,description='Id of the patient in the DB',example='P001')):
    # load the patients data
    data = load_data()
    if patients_id in data:
        return data[patients_id]
    raise HTTPException(status_code=404,detail='Patient Not fund')

@app.get('/sort')
def sort_patients(
    sort_by: str = Query(..., description='Sort on the basis of height,weight or bmi'),
    order: str = Query('asc', description='sort in asc or desc')
):

    valid_fields = ['height','weight','bmi']
    if sort_by not in valid_fields:
        raise HTTPException(status_code=400,detail=f'invalid field select from {valid_fields}')
    if order not in ['asc','desc']:
        raise HTTPException(status_code=400,detail='invalid order select asc or desc')
    
    data = load_data()
    
    sort_order = True if order == 'desc' else False
    sorted_data = sorted(data.values(), key=lambda x: x.get(sort_by, 0), reverse=sort_order)
    
    return sorted_data