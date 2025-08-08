from fastapi import Path,Query,HTTPException,FastAPI
from pydantic import BaseModel,Field,computed_field
from fastapi.responses import JSONResponse
from typing import Annotated,Literal,Optional
import json

app = FastAPI()


class Patient(BaseModel):
    
    id:Annotated[str,Field(...,description='Id of the patient',examples=['P001'])]
    name:Annotated[str,Field(...,description='Name of the patient',examples=['Atiq'])] 
    city:Annotated[str,Field(...,description='City of the pattient',examples=['Bannu'])]
    age:Annotated[int,Field(...,description='Age of the patient',gt=0,lt=60)]
    gender:Annotated[Literal['male','female','others'],Field(...,description='Gender of the patien')]
    height:Annotated[float,Field(...,gt=0,description='Height of the patient in mtrs')]
    weight:Annotated[float,Field(...,gt=0,description='Weight of the patient in kgs')]
    
    @computed_field()
    @property
    def bmi(self) -> float:
        bmi= round(self.weight / (self.height ** 2), 2)
        return bmi
    
    
    @computed_field()
    @property
    def verdict(self) -> str:
        if self.bmi < 18.5:
            return 'Underweighted'
        elif self.bmi < 25 :
            return 'Normal'
        elif self.bmi < 30:
            return 'Normal'
        else:
            return 'Obese'


class PatientUpdate(BaseModel):
    name:Annotated[Optional[str],Field(default=None)] 
    city:Annotated[Optional[str],Field(default=None)]
    age:Annotated[Optional[int],Field(default=None,gt=0)]
    gender:Annotated[Optional[Literal['male','female','others']],Field(default=None)]
    height:Annotated[Optional[float],Field(default=None,gt=0,)]
    weight:Annotated[Optional[float],Field(default=None,gt=0,)]
    
    
def load_data():
    with open('patients.json','r') as f:
        data = json.load(f)
    return data

def save_data(data):
    with open('patients.json', 'w') as f:
        json.dump(data, f)

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

@app.post('/create')
def create_patient(patient: Patient):

    # load existing data
    data = load_data()

    # check if the patient already exists
    if patient.id in data:
        raise HTTPException(status_code=400, detail='Patient already exists')

    # new patient add to the database
    data[patient.id] = patient.model_dump(exclude=['id'])

    # save into the json file
    save_data(data)
    
    
@app.put('/edit/{patient_id}')
def patient_update(patient_id:str , update_patient:PatientUpdate):
    
    # load the existing data
    data = load_data()
    
    # here first we will check is the patient exist in the db
    if patient_id not in data:
        raise HTTPException(status_code=404,detail='Patient not Fund')
    existing_patient_info = data[patient_id]
    # here first we have to convert the model into dict then it wii be easy
    updated_patient_info = update_patient.model_dump(exclude_unset=True)
    
    for key,value in updated_patient_info.items():
        existing_patient_info[key] = value
        
    existing_patient_info['id'] = patient_id
    patient_pydantic_object = Patient(**existing_patient_info)
    existing_patient_info=patient_pydantic_object.model_dump(exclude='id')
    
    data[patient_id] = existing_patient_info
    
    save_data(data)
    
    return JSONResponse(status_code=200,content={'meesage':'Patient updated successfuly'})

@app.delete('/delete/{patient_id}')
def delete_patient(patient_id:str):
    
    data = load_data()
    
    if patient_id not in data:
        raise HTTPException(status_code=404,detail='patient not fund')
    del data[patient_id]
    
    save_data(data)
    
    return JSONResponse(status_code=200,content={'message':'Patient Deleted Successfully'})