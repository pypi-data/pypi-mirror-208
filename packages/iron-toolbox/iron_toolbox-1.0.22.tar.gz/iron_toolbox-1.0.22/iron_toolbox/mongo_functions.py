import pymongo
import pandas as pd
import os
from tqdm import tqdm

client = pymongo.MongoClient(os.environ["MONGO_PROD_URL"], port=27017, compressors='zlib', zlibCompressionLevel=1)
db = client.parse_db
print(client.server_info())

''' Funções para download de collections do Mongo '''


def create_table_schema(mongodb_collection):
    schema = []
    if mongodb_collection == 'Support':
        schema = {'_id', '_p_activeStaff', 'job', '_p_patient', '_created_at', '_updated_at', '_p_support', 'startTime',
                  'endTime', 'duration', 'waitingTime', 'status', 'isTransfer', 'rating', 'review', 'fup24', 'fup48',
                  'description', 'symptomsStarted', 'complains', 'exams', 'orientations', 'isGiftCard', 'cid10', 'ciap',
                  'videoEctoscopicExams', 'outsideAppointments', 'illnessAllergies', 'medicines', 'additionalNotes'}

    if mongodb_collection == 'UserTelephoneCall':
        schema = {'_created_at', '_p_corporation', 'date', '_p_staff', '_p_responsible', '_p_scheduledAppointments',
                  '_p_support', '_p_user', '_updated_at', 'additionalComments', 'duplicatedFlag', 'reason', 'title',
                  'end_time', 'start_time', 'CIDdiagnose', 'CIAPdiagnose', 'contactChannel', 'status', 'serviceReturn',
                  'complains', 'orientations', 'exams', 'medicines', 'fup', 'illnessAllergies', 'note'}

    dataframe = pd.DataFrame(columns=schema)
    return dataframe


def contar_itens_collection(filtro, mongodb_collection):
    if filtro is None:
        doc_count = db[mongodb_collection].count_documents({})
    else:
        doc_count = db[mongodb_collection].count_documents(filtro)
    print(f'\nNúmero de itens na Collection {mongodb_collection}: {doc_count}')
    return doc_count


def gerar_data_do_ultimo_registro(mongodb_collection):
    data_ultimo_registo = pd.DataFrame(db[mongodb_collection].find({}, {'_updated_at': 1}).sort([('_updated_at',
                                                                                                  -1)]).limit(1))
    return data_ultimo_registo


def gerar_tabela_schema(mongodb_collection='_SCHEMA'):
    contar_itens_collection(filtro=None, mongodb_collection=mongodb_collection)
    dbSchema = pd.DataFrame(tqdm(db[mongodb_collection].find({})))
    print(f'Dataset {mongodb_collection} Criado!')
    return dbSchema


def gerar_tabela_support(filtro=None, colunas=None, mongodb_collection='Support'):
    contar_itens_collection(filtro, mongodb_collection)
    dbsupport_schema = create_table_schema(mongodb_collection)
    if colunas is None:
        dbsupport = pd.DataFrame(tqdm(db['Support'].find(filtro, {'_id': 1,
                                                                  '_p_activeStaff': 1,
                                                                  'job': 1,
                                                                  '_p_patient': 1,
                                                                  '_created_at': 1,
                                                                  '_updated_at': 1,
                                                                  '_p_support': 1,
                                                                  'startTime': 1,
                                                                  'endTime': 1,
                                                                  'duration': 1,
                                                                  'waitingTime': 1,
                                                                  'status': 1,
                                                                  'isTransfer': 1,
                                                                  'rating': 1,
                                                                  'review': 1,
                                                                  'fup24': 1,
                                                                  'fup48': 1,
                                                                  'symptomsStarted': 1,
                                                                  'complains': 1,
                                                                  'exams': 1,
                                                                  'orientations': 1,
                                                                  'videoEctoscopicExams': 1,
                                                                  'isGiftCard': 1,
                                                                  'outsideAppointments': 1,
                                                                  'illnessAllergies': 1,
                                                                  'medicines': 1,
                                                                  'additionalNotes': 1,
                                                                  'description': 1,
                                                                  'cid10': 1,
                                                                  'ciap': 1}), desc="Total itens recebidos:"))
        print(f'Realizando tratamento do Dataset {mongodb_collection}!')
        dbsupport = dbsupport.replace({'_p_patient': r'^_User\$'}, {'_p_patient': ''}, regex=True)
        dbsupport = dbsupport.replace({'_p_activeStaff': r'^Staff\$'}, {'_p_activeStaff': ''}, regex=True)
        dbsupport = dbsupport.replace({'_p_support': r'^Support\$'}, {'_p_support': ''}, regex=True)
        dbsupport = pd.concat([dbsupport, dbsupport_schema])
    else:
        dbsupport = pd.DataFrame(tqdm(db[mongodb_collection].find(filtro, colunas), desc="Total itens recebidos:"))
    # adicionar o tratamento fora do if com uma condicao de teste
    print(f'Dataset {mongodb_collection} Criado!')
    return dbsupport


def gerar_tabela_corporation(filtro=None, colunas=None, mongodb_collection='Corporation'):
    contar_itens_collection(filtro, mongodb_collection)
    if colunas is None:
        dbCorporation = pd.DataFrame(tqdm(db[mongodb_collection].find(filtro, {'_id': 1,
                                                                               'name': 1,
                                                                               '_created_at': 1,
                                                                               '_updated_at': 1,
                                                                               'job': 1}),
                                          desc="Total itens recebidos:"))
        print(f'Realizando tratamento do Dataset {mongodb_collection}!')
    else:
        dbCorporation = pd.DataFrame(tqdm(db[mongodb_collection].find(filtro, colunas), desc="Total itens recebidos:"))
    print(f'Dataset {mongodb_collection} Criado!')
    return dbCorporation


def gerar_tabela_corporation_pin(filtro=None, colunas=None, mongodb_collection='CorporationPin'):
    contar_itens_collection(filtro, mongodb_collection)
    if colunas is None:
        dbCorporationPin = pd.DataFrame(tqdm(db[mongodb_collection].find(filtro, {'_id': 1,
                                                                                  'pin': 1,
                                                                                  'userNumber': 1,
                                                                                  'email': 1,
                                                                                  'name': 1,
                                                                                  '_p_corporation': 1,
                                                                                  'cpf': 1,
                                                                                  'isValid': 1,
                                                                                  'unsubscribed': 1,
                                                                                  '_created_at': 1,
                                                                                  '_p_user': 1,
                                                                                  '_updated_at': 1}),
                                             desc="Total itens recebidos:"))

        dbCorporationPin = dbCorporationPin.replace({'_p_user': r'^_User\$'}, {'_p_user': ''}, regex=True)
    else:
        dbCorporationPin = pd.DataFrame(tqdm(db[mongodb_collection].find(filtro, colunas),
                                             desc="Total itens recebidos:"))
    print(f'Dataset {mongodb_collection} Criado!')
    return dbCorporationPin


def gerar_tabela_user(filtro=None, colunas=None, mongodb_collection='_User'):
    contar_itens_collection(filtro, mongodb_collection)
    if colunas is None:
        dbUser = pd.DataFrame(tqdm(db[mongodb_collection].find(filtro, {'_id': 1,
                                                                        'name': 1,
                                                                        'cpf': 1,
                                                                        'useremail': 1,
                                                                        'externalId': 1,
                                                                        '_p_corporation': 1,
                                                                        '_p_userPublic': 1,
                                                                        'mainRole': 1,
                                                                        '_created_at': 1,
                                                                        '_updated_at': 1,
                                                                        'isDependent': 1,
                                                                        'family_id': 1,
                                                                        'familyNames': 1,
                                                                        'numeroCartao': 1,
                                                                        'isAdmaUser': 1,
                                                                        'isBlocked': 1,
                                                                        'termsOfsubscription': 1,
                                                                        'consentTerm': 1,
                                                                        'isDeleted': 1,
                                                                        'organizationCNPJ': 1,
                                                                        'organizationDepartment': 1,
                                                                        'organizationDescription': 1,
                                                                        'organizationOperator': 1,
                                                                        'organizationPlan': 1,
                                                                        'organizationRole': 1,
                                                                        'organizationUnity': 1,
                                                                        'organizationCNAE': 1,
                                                                        'customData': 1,
                                                                        'isStaff': 1}), desc="Total itens recebidos:"))

        dbUser = dbUser.replace({'_p_corporation': r'^Corporation\$'}, {'_p_corporation': ''}, regex=True)
        dbUser = dbUser.replace({'_p_userPublic': r'^UserPublic\$'}, {'_p_userPublic': ''}, regex=True)
    else:
        dbUser = pd.DataFrame(tqdm(db[mongodb_collection].find(filtro, colunas), desc="Total itens recebidos:"))

    for i, row in dbUser.iterrows():
        try:
            dbUser['NOME_PACIENTE'][i] = dbUser['NOME_PACIENTE'][i].upper().strip()
        except:
            continue
    print(f'Dataset {mongodb_collection} Criado!')
    return dbUser


def gerar_tabela_user_phone(filtro=None, colunas=None, mongodb_collection='UserPhone'):
    contar_itens_collection(filtro, mongodb_collection)
    dbUserPhone = pd.DataFrame()
    if colunas is None:
        UserPhone = pd.DataFrame(tqdm(db[mongodb_collection].find({}, {'_id': 1,
                                                                       '_created_at': 1,
                                                                       '_updated_at': 1,
                                                                       '_p_user': 1,
                                                                       'primary': 1,
                                                                       'number': 1}), desc="Total itens recebidos:"))

        print(f'Realizando tratamento do Dataset {mongodb_collection}!')
        UserPhone = UserPhone.replace({'_p_user': r'^_User\$'}, {'_p_user': ''}, regex=True)
        UserPhone.sort_values(['_p_user', '_created_at'], inplace=True)

        UserPhone_true = UserPhone.loc[UserPhone['primary'] == True]
        UserPhone_true.drop_duplicates(['_p_user'], keep='last', inplace=True)
        UserPhone_true.rename(columns={'number': 'phone_number_01'}, inplace=True)

        UserPhone_false = UserPhone.loc[UserPhone['primary'] == False]
        UserPhone_false.drop_duplicates(['_p_user'], keep='last', inplace=True)
        UserPhone_false = UserPhone_false[['_p_user', 'number']]
        UserPhone_false.rename(columns={'number': 'phone_number_02'}, inplace=True)
        if len(UserPhone_false) > 1:
            dbUserPhone = pd.merge(UserPhone_true, UserPhone_false, how="outer", on=['_p_user']).reset_index(drop=True)
        else:
            dbUserPhone = UserPhone_true

        dbUserPhone.drop(columns=['primary'])

    else:
        dbUser = pd.DataFrame(tqdm(db[mongodb_collection].find(filtro, colunas), desc="Total itens recebidos:"))
    print(f'Dataset {mongodb_collection} Criado!')
    return dbUserPhone


def gerar_tabela_user_contract(filtro=None, colunas=None, mongodb_collection='UserContract'):
    contar_itens_collection(filtro, mongodb_collection)
    dbUserContract = pd.DataFrame()
    if colunas is None:
        dbUserContract = pd.DataFrame(tqdm(db[mongodb_collection].find(filtro), desc="Total itens recebidos:"))
        dbUserContract = dbUserContract.replace({'_p_user': r'^_User\$'}, {'_p_user': ''}, regex=True)
        print(f'Dataset {mongodb_collection} Criado!')
    else:
        print('Nesta Collection ainda não é possivel escolher as colunas')
    return dbUserContract


def gerar_tabela_user_adress(filtro=None, colunas=None, mongodb_collection='UserAddress'):
    contar_itens_collection(filtro, mongodb_collection)
    if colunas is None:
        dbUserAddress = pd.DataFrame(tqdm(db[mongodb_collection].find(filtro), desc="Total itens recebidos:"))
        dbUserAddress = dbUserAddress.replace({'_p_user': r'^_User\$'}, {'_p_user': ''}, regex=True)
        print(f'Dataset {mongodb_collection} Criado!')
    else:
        print('Nesta Collection ainda não é possivel escolher as colunas')
    return dbUserAddress


def gerar_tabela_user_public(filtro=None, colunas=None, mongodb_collection='UserPublic'):
    contar_itens_collection(filtro, mongodb_collection)
    if colunas is None:
        dbUserPublic = pd.DataFrame(tqdm(db[mongodb_collection].find(filtro), desc="Total itens recebidos:"))
        print(f'Dataset {mongodb_collection} Criado!')
    else:
        print('Nesta Collection ainda não é possivel escolher as colunas')
    return dbUserPublic


def gerar_tabela_user_sicknote(filtro=None, colunas=None, mongodb_collection='UserSickNote'):
    contar_itens_collection(filtro, mongodb_collection)
    if colunas is None:
        dbUserSickNote = pd.DataFrame(tqdm(db[mongodb_collection].find(filtro, {'_id': 1,
                                                                                '_created_at': 1,
                                                                                '_p_CID10': 1,
                                                                                '_p_doctor': 1,
                                                                                '_p_support': 1,
                                                                                '_p_appointmentId': 1,
                                                                                '_p_telephonecallId': 1,
                                                                                '_p_user': 1,
                                                                                'date': 1,
                                                                                'days': 1,
                                                                                'document': 1,
                                                                                'city': 1,
                                                                                'uf': 1,
                                                                                'name': 1,
                                                                                'file': 1,
                                                                                '_updated_at': 1}),
                                           desc="Total itens recebidos:"))

        dbUserSickNote = dbUserSickNote.replace({'_p_user': r'^_User\$'}, {'_p_user': ''}, regex=True)
        dbUserSickNote = dbUserSickNote.replace({'_p_CID10': r'^CID10\$'}, {'_p_CID10': ''}, regex=True)
        dbUserSickNote = dbUserSickNote.replace({'_p_doctor': r'^Staff\$'}, {'_p_doctor': ''}, regex=True)
        dbUserSickNote = dbUserSickNote.replace({'_p_appointmentId': r'^ScheduledAppointments\$'},
                                                {'_p_appointmentId': ''}, regex=True)
        dbUserSickNote = dbUserSickNote.replace({'_p_support': r'^Support\$'}, {'_p_support': ''}, regex=True)
        dbUserSickNote = dbUserSickNote.replace({'_p_appointmentId': r'^ScheduledAppointments\$'},
                                                {'_p_appointmentId': ''}, regex=True)
        dbUserSickNote = dbUserSickNote.replace({'_p_telephonecallId': r'^UserTelephoneCall\$'},
                                                {'_p_telephonecallId': ''}, regex=True)

    else:
        dbUserSickNote = pd.DataFrame(tqdm(db[mongodb_collection].find(filtro, colunas), desc="Total itens recebidos:"))
    print(f'Dataset {mongodb_collection} Criado!')
    return dbUserSickNote


def gerar_tabela_user_outside_appointment(filtro=None, colunas=None, mongodb_collection='UserOutsideAppointment'):
    contar_itens_collection(filtro, mongodb_collection)
    if colunas is None:
        dbUserOutsideAppointment = pd.DataFrame(tqdm(db[mongodb_collection].find(filtro, {'_id': 1,
                                                                                          '_created_at': 1,
                                                                                          '_p_createdBy': 1,
                                                                                          '_p_doctorPatient': 1,
                                                                                          '_p_user': 1,
                                                                                          '_updated_at': 1,
                                                                                          'date': 1,
                                                                                          'isCanceled': 1,
                                                                                          'isCompleted': 1,
                                                                                          'entryCollection': 1,
                                                                                          'entryObjectId': 1,
                                                                                          'isDeleted': 1,
                                                                                          'forwardingType': 1,
                                                                                          'speciality': 1,
                                                                                          '_p_scheduledAppointment': 1,
                                                                                          'note': 1,
                                                                                          '_p_support': 1,
                                                                                          '_p_appointmentId': 1,
                                                                                          '_p_telephonecallId': 1}),
                                                     desc="Total itens recebidos:"))

        dbUserOutsideAppointment = dbUserOutsideAppointment.replace({'_p_user': r'^_User\$'}, {'_p_user': ''},
                                                                    regex=True)
        dbUserOutsideAppointment = dbUserOutsideAppointment.replace({'_p_doctorPatient': r'^DoctorPatient\$'},
                                                                    {'_p_doctorPatient': ''}, regex=True)
        dbUserOutsideAppointment = dbUserOutsideAppointment.replace({'_p_createdBy': r'^Staff\$'}, {'_p_createdBy': ''},
                                                                    regex=True)
        dbUserOutsideAppointment = dbUserOutsideAppointment.replace({'_p_scheduledAppointment':
                                                                    r'^ScheduledAppointments\$'},
                                                                    {'_p_scheduledAppointment': ''}, regex=True)
        dbUserOutsideAppointment = dbUserOutsideAppointment.replace({'_p_support': r'^Support\$'}, {'_p_support': ''},
                                                                    regex=True)
        dbUserOutsideAppointment = dbUserOutsideAppointment.replace({'_p_appointmentId': r'^ScheduledAppointments\$'},
                                                                    {'_p_appointmentId': ''}, regex=True)
        dbUserOutsideAppointment = dbUserOutsideAppointment.replace({'_p_telephonecallId': r'^UserTelephoneCall\$'},
                                                                    {'_p_telephonecallId': ''}, regex=True)
    else:
        dbUserOutsideAppointment = pd.DataFrame(tqdm(db[mongodb_collection].find(filtro, colunas),
                                                     desc="Total itens recebidos:"))
    print(f'Dataset {mongodb_collection} Criado!')
    return dbUserOutsideAppointment


def gerar_tabela_family(filtro=None, colunas=None, mongodb_collection='Family'):
    contar_itens_collection(filtro, mongodb_collection)
    dbFamily = pd.DataFrame(tqdm(db[mongodb_collection].find(filtro, colunas), desc="Total itens recebidos:"))
    print(f'Dataset {mongodb_collection} Criado!')
    return dbFamily


def gerar_tabela_cid10(filtro=None, colunas=None, mongodb_collection='CID10'):
    contar_itens_collection(filtro, mongodb_collection)
    if colunas is None:
        dbCID10 = pd.DataFrame(tqdm(db[mongodb_collection].find({}, {'_id': 1,
                                                                     '_created_at': 1,
                                                                     '_updated_at': 1,
                                                                     'code': 1,
                                                                     'description': 1,
                                                                     'is_chronic': 1}), desc="Total itens recebidos:"))
        print(f'Dataset {mongodb_collection} Criado!')
    else:
        dbCID10 = pd.DataFrame(tqdm(db[mongodb_collection].find(filtro, colunas), desc="Total itens recebidos:"))
        print(f'Dataset {mongodb_collection} Criado!')
    return dbCID10


def gerar_tabela_ciap(filtro=None, colunas=None, mongodb_collection='CIAP'):
    contar_itens_collection(filtro, mongodb_collection)
    if colunas is None:
        dbCIAP = pd.DataFrame(tqdm(db[mongodb_collection].find({}, {}), desc="Total itens recebidos:"))
        print(f'Dataset {mongodb_collection} Criado!')
    else:
        dbCIAP = pd.DataFrame(tqdm(db[mongodb_collection].find(filtro, colunas), desc="Total itens recebidos:"))
        print('Nesta Collection ainda não é possivel escolher as colunas')
    return dbCIAP


def gerar_tabela_staff(filtro=None, colunas=None, mongodb_collection='Staff'):
    contar_itens_collection(filtro, mongodb_collection)
    contar_itens_collection(filtro, mongodb_collection)
    if colunas is None:
        dbStaff = pd.DataFrame(tqdm(db[mongodb_collection].find({}, {'_id': 1,
                                                                     '_created_at': 1,
                                                                     '_updated_at': 1,
                                                                     'name': 1,
                                                                     'isBlocked': 1,
                                                                     'isDeleted': 1,
                                                                     'job': 1,
                                                                     'department': 1,
                                                                     'register': 1,
                                                                     'email': 1,
                                                                     '_p_user': 1,
                                                                     'phone': 1,
                                                                     'siglaConselho': 1,
                                                                     'numeroConselho': 1,
                                                                     'siglaEstadoConselho': 1,
                                                                     '_p_corporation': 1,
                                                                     'liveSupport': 1,
                                                                     'cbo': 1}), desc="Total itens recebidos:"))

        dbStaff = dbStaff.replace({'_p_user': r'^_User\$'}, {'_p_user': ''}, regex=True)
        dbStaff = dbStaff.replace({'_p_corporation': r'^Corporation\$'}, {'_p_corporation': ''}, regex=True)
    else:
        dbStaff = pd.DataFrame(tqdm(db[mongodb_collection].find(filtro, colunas), desc="Total itens recebidos:"))
    print(f'Dataset {mongodb_collection} Criado!')
    return dbStaff


def gerar_tabela_staff_cbo(filtro=None, colunas=None, mongodb_collection='StaffCBO'):
    contar_itens_collection(filtro, mongodb_collection)
    if colunas is None:
        dbStaffCBO = pd.DataFrame(tqdm(db[mongodb_collection].find({}, {'_id': 1,
                                                                        '_created_at': 1,
                                                                        '_updated_at': 1,
                                                                        'code': 1,
                                                                        'title': 1}), desc="Total itens recebidos:"))
    else:
        dbStaffCBO = pd.DataFrame(tqdm(db[mongodb_collection].find(filtro, colunas), desc="Total itens recebidos:"))
    print(f'Dataset {mongodb_collection} Criado!')
    return dbStaffCBO


def gerar_tabela_doctor_patient(filtro=None, colunas=None, mongodb_collection='DoctorPatient'):
    contar_itens_collection(filtro, mongodb_collection)
    if colunas is None:
        dbDoctorPatient = pd.DataFrame(tqdm(db[mongodb_collection].find({}, {'_id': 1,
                                                                             '_created_at': 1,
                                                                             '_updated_at': 1,
                                                                             '_p_corporation': 1,
                                                                             '_p_doctor': 1,
                                                                             '_p_patient': 1,
                                                                             'healthProfile': 1,
                                                                             'healthProfileHistory': 1,
                                                                             'status': 1}),
                                            desc="Total itens recebidos:"))

        dbDoctorPatient = dbDoctorPatient.replace({'_p_doctor': r'^Staff\$'}, {'_p_doctor': ''}, regex=True)
        dbDoctorPatient = dbDoctorPatient.replace({'_p_patient': r'^_User\$'}, {'_p_patient': ''}, regex=True)
        dbDoctorPatient = dbDoctorPatient.replace({'_p_corporation': r'^Corporation\$'}, {'_p_corporation': ''},
                                                  regex=True)
    else:
        dbDoctorPatient = pd.DataFrame(tqdm(db[mongodb_collection].find(filtro, colunas),
                                            desc="Total itens recebidos:"))
    print(f'Dataset {mongodb_collection} Criado!')
    return dbDoctorPatient


def gerar_tabela_user_health_complain(filtro=None, colunas=None, mongodb_collection='UserHealthComplain'):
    contar_itens_collection(filtro, mongodb_collection)
    if colunas is None:
        dbUserHealthComplain = pd.DataFrame(tqdm(db[mongodb_collection].find(filtro, {'_id': 1,
                                                                                      '_created_at': 1,
                                                                                      '_updated_at': 1,
                                                                                      '_p_patient': 1,
                                                                                      '_p_doctorPatient': 1,
                                                                                      'date': 1,
                                                                                      'name': 1,
                                                                                      'isDeleted': 1,
                                                                                      '_p_createdBy': 1,
                                                                                      'description': 1,
                                                                                      'code': 1}),
                                                 desc="Total itens recebidos:"))

        dbUserHealthComplain = dbUserHealthComplain.replace({'_p_patient': r'^_User\$'}, {'_p_patient': ''}, regex=True)
        dbUserHealthComplain = dbUserHealthComplain.replace({'_p_doctorPatient': r'^DoctorPatient\$'},
                                                            {'_p_doctorPatient': ''}, regex=True)
        dbUserHealthComplain = dbUserHealthComplain.replace({'_p_createdBy': r'^Staff\$'}, {'_p_createdBy': ''},
                                                            regex=True)
    else:
        dbUserHealthComplain = pd.DataFrame(tqdm(db[mongodb_collection].find(filtro, colunas),
                                                 desc="Total itens recebidos:"))
    print(f'Dataset {mongodb_collection} Criado!')
    return dbUserHealthComplain


def gerar_tabela_user_telephone_call(filtro=None, colunas=None, mongodb_collection='UserTelephoneCall'):
    contar_itens_collection(filtro, mongodb_collection)
    dbusertelephonecall_schema = create_table_schema(mongodb_collection)
    if colunas is None:
        dbusertelephonecall = pd.DataFrame(tqdm(db[mongodb_collection].find(filtro, {'_id': 1,
                                                                                     '_created_at': 1,
                                                                                     '_p_corporation': 1,
                                                                                     'date': 1,
                                                                                     '_p_staff': 1,
                                                                                     '_p_responsible': 1,
                                                                                     '_p_scheduledAppointments': 1,
                                                                                     '_p_support': 1,
                                                                                     '_p_user': 1,
                                                                                     '_updated_at': 1,
                                                                                     'additionalComments': 1,
                                                                                     'duplicatedFlag': 1,
                                                                                     'reason': 1,
                                                                                     'title': 1,
                                                                                     'end_time': 1,
                                                                                     'start_time': 1,
                                                                                     'CIDdiagnose': 1,
                                                                                     'CIAPdiagnose': 1,
                                                                                     'contactChannel': 1,
                                                                                     'status': 1,
                                                                                     'serviceReturn': 1,
                                                                                     'complains': 1,
                                                                                     'orientations': 1,
                                                                                     'exams': 1,
                                                                                     'medicines': 1,
                                                                                     'outsideAppointments': 1,
                                                                                     'fup': 1,
                                                                                     'illnessAllergies': 1,
                                                                                     'linkedMedicine': 1,
                                                                                     'linkedSickNote': 1,
                                                                                     'note': 1}),
                                                desc="Total itens recebidos:"))
        print(f'Realizando tratamento do Dataset {mongodb_collection}!')
        dbusertelephonecall = dbusertelephonecall.replace({'_p_support': r'^Support\$'}, {'_p_support': ''}, regex=True)
        dbusertelephonecall = dbusertelephonecall.replace({'_p_scheduledAppointments': r'^ScheduledAppointments\$'},
                                                          {'_p_scheduledAppointments': ''}, regex=True)
        dbusertelephonecall = dbusertelephonecall.replace({'_p_staff': r'^Staff\$'}, {'_p_staff': ''}, regex=True)
        dbusertelephonecall = dbusertelephonecall.replace({'_p_responsible': r'^Staff\$'}, {'_p_responsible': ''},
                                                          regex=True)
        dbusertelephonecall = dbusertelephonecall.replace({'_p_user': r'^_User\$'}, {'_p_user': ''}, regex=True)
        dbusertelephonecall = dbusertelephonecall.replace({'_p_corporation': r'^Corporation\$'},
                                                                  {'_p_corporation': ''}, regex=True)
        dbusertelephonecall = pd.concat([dbusertelephonecall, dbusertelephonecall_schema])
    else:
        dbusertelephonecall = pd.DataFrame(tqdm(db[mongodb_collection].find(filtro, colunas),
                                                desc="Total itens recebidos:"))
        dbusertelephonecall = dbusertelephonecall.replace({'_p_support': r'^Support\$'}, {'_p_support': ''}, regex=True)
        dbusertelephonecall = dbusertelephonecall.replace({'_p_staff': r'^Staff\$'}, {'_p_staff': ''}, regex=True)
        dbusertelephonecall = dbusertelephonecall.replace({'_p_user': r'^_User\$'}, {'_p_user': ''}, regex=True)


    print(f'Dataset {mongodb_collection} Criado!')
    return dbusertelephonecall


def gerar_tabela_scheduled_appointments(filtro=None, colunas=None, mongodb_collection='ScheduledAppointments'):
    contar_itens_collection(filtro, mongodb_collection)
    if colunas is None:
        dbScheduledAppointments = pd.DataFrame(tqdm(db[mongodb_collection].find(filtro, {'_id': 1,
                                                                                         'UTCdatetime': 1,
                                                                                         '_created_at': 1,
                                                                                         '_p_activeStaff': 1,
                                                                                         '_p_corporation': 1,
                                                                                         '_p_patient': 1,
                                                                                         '_updated_at': 1,
                                                                                         'appointmentDate': 1,
                                                                                         'appointmentEndTime': 1,
                                                                                         'appointmentStartTime': 1,
                                                                                         'cancelledAppointmentDate': 1,
                                                                                         '_p_deletedBy': 1,
                                                                                         'isTransfer': 1,
                                                                                         'job': 1,
                                                                                         'staffSpeciality': 1,
                                                                                         '_p_createdBy': 1,
                                                                                         'status': 1,
                                                                                         'type': 1,
                                                                                         'waitingTime': 1,
                                                                                         'complains': 1,
                                                                                         'exams': 1,
                                                                                         'note': 1,
                                                                                         'orientations': 1,
                                                                                         'videoEctoscopicExams': 1,
                                                                                         'outsideAppointments': 1,
                                                                                         'medicines': 1,
                                                                                         'appointmentOrigin': 1}),
                                                    desc="Total itens recebidos:"))
        print(f'Realizando tratamento do Dataset {mongodb_collection}!')
        dbScheduledAppointments = dbScheduledAppointments.replace({'_p_activeStaff': r'^ScheduledStaff\$'},
                                                                  {'_p_activeStaff': ''}, regex=True)
        dbScheduledAppointments = dbScheduledAppointments.replace({'_p_patient': r'^_User\$'}, {'_p_patient': ''},
                                                                  regex=True)
        dbScheduledAppointments = dbScheduledAppointments.replace({'_p_createdBy': r'^_User\$'}, {'_p_createdBy': ''},
                                                                  regex=True)
        dbScheduledAppointments = dbScheduledAppointments.replace({'_p_deletedBy': r'^_User\$'}, {'_p_deletedBy': ''},
                                                                  regex=True)
        dbScheduledAppointments = dbScheduledAppointments.replace({'_p_corporation': r'^Corporation\$'},
                                                                  {'_p_corporation': ''}, regex=True)
    else:
        dbScheduledAppointments = pd.DataFrame(tqdm(db[mongodb_collection].find(filtro, colunas),
                                                    desc="Total itens recebidos:"))
    print(f'Dataset {mongodb_collection} Criado!')
    return dbScheduledAppointments


def gerar_tabela_scheduling_report(filtro=None, colunas=None, mongodb_collection='SchedulingReport'):
    contar_itens_collection(filtro, mongodb_collection)
    if colunas is None:
        dbSchedulingReport = pd.DataFrame(tqdm(db[mongodb_collection].find(filtro, {'_id': 1,
                                                                                    'PatientEmail': 1,
                                                                                    'PatientPhone': 1,
                                                                                    '_created_at': 1,
                                                                                    '_p_corporation': 1,
                                                                                    '_p_patient': 1,
                                                                                    '_p_scheduleAppointment': 1,
                                                                                    '_p_staff': 1,
                                                                                    '_updated_at': 1,
                                                                                    'appointmentDate': 1,
                                                                                    'duration': 1,
                                                                                    'patientName': 1,
                                                                                    'staffSpeciality': 1,
                                                                                    'staffState': 1,
                                                                                    'status': 1,
                                                                                    'totalCompletedCalls': 1,
                                                                                    '_p_scheduleCallLogs': 1,
                                                                                    'endTime': 1,
                                                                                    'startTime': 1,
                                                                                    'doctor_review': 1,
                                                                                    'patient_review': 1,
                                                                                    'patient_rating': 1,
                                                                                    'additionalNotes': 1}),
                                               desc="Total itens recebidos:"))
        print(f'Realizando tratamento do Dataset {mongodb_collection}!')
        dbSchedulingReport = dbSchedulingReport.replace({'_p_activeStaff': r'^ScheduledStaff\$'},
                                                        {'_p_activeStaff': ''}, regex=True)
        dbSchedulingReport = dbSchedulingReport.replace({'_p_patient': r'^_User\$'}, {'_p_patient': ''},
                                                        regex=True)
        dbSchedulingReport = dbSchedulingReport.replace({'_p_corporation': r'^Corporation\$'},
                                                        {'_p_corporation': ''}, regex=True)
        dbSchedulingReport = dbSchedulingReport.replace({'_p_scheduledAppointment': r'^ScheduledAppointments\$'},
                                                        {'_p_scheduledAppointment': ''}, regex=True)
        dbSchedulingReport = dbSchedulingReport.replace({'_p_scheduleAppointment': r'^ScheduledAppointments\$'},
                                                        {'_p_scheduleAppointment': ''}, regex=True)
        dbSchedulingReport = dbSchedulingReport.replace({'_p_staff': r'^ScheduledStaff\$'}, {'_p_staff': ''},
                                                        regex=True)
    else:
        dbSchedulingReport = pd.DataFrame(
            tqdm(db[mongodb_collection].find(filtro, colunas), desc="Total itens recebidos:"))
    print(f'Dataset {mongodb_collection} Criado!')
    return dbSchedulingReport


def gerar_tabela_user_health_analyze(filtro=None, colunas=None, mongodb_collection='UserHealthAnalyze'):
    contar_itens_collection(filtro, mongodb_collection)
    if colunas is None:
        dbUserHealthAnalyze = pd.DataFrame(tqdm(db[mongodb_collection].find(filtro, {'id': 1,
                                                                                     '_created_at': 1,
                                                                                     '_p_corporation': 1,
                                                                                     '_p_doctorPatient': 1,
                                                                                     '_p_staff': 1,
                                                                                     '_p_user': 1,
                                                                                     '_updated_at': 1,
                                                                                     'cidCode': 1,
                                                                                     'cidDescription': 1,
                                                                                     'date': 1,
                                                                                     'groupName': 1,
                                                                                     'isAnalysed': 1,
                                                                                     'isDeleted': 1,
                                                                                     'isPending': 1,
                                                                                     'observation': 1,
                                                                                     'orientation': 1,
                                                                                     'staffName': 1,
                                                                                     'tag': 1,
                                                                                     'title': 1,
                                                                                     'tussCode': 1,
                                                                                     'tussCodeDescription': 1,
                                                                                     'type': 1,
                                                                                     '_p_supportId': 1,
                                                                                     '_p_clinicalExam': 1,
                                                                                     '_p_support': 1,
                                                                                     '_p_appointmentId': 1,
                                                                                     '_p_telephonecallId': 1}),
                                                desc="Total itens recebidos:"))
        print(f'Realizando tratamento do Dataset {mongodb_collection}!')
        dbUserHealthAnalyze = dbUserHealthAnalyze.replace({'_p_corporation': r'^Corporation\$'}, {'_p_corporation': ''},
                                                          regex=True)
        dbUserHealthAnalyze = dbUserHealthAnalyze.replace({'_p_doctorPatient': r'^DoctorPatient\$'},
                                                          {'_p_doctorPatient': ''}, regex=True)
        dbUserHealthAnalyze = dbUserHealthAnalyze.replace({'_p_staff': r'^Staff\$'}, {'_p_staff': ''}, regex=True)
        dbUserHealthAnalyze = dbUserHealthAnalyze.replace({'_p_user': r'^_User\$'}, {'_p_user': ''}, regex=True)
        dbUserHealthAnalyze = dbUserHealthAnalyze.replace({'_p_clinicalExam': r'^CatalogClinicalExam\$'},
                                                          {'_p_clinicalExam': ''},regex=True)
        dbUserHealthAnalyze = dbUserHealthAnalyze.replace({'_p_supportId': r'^Support\$'}, {'_p_supportId': ''},
                                                          regex=True)
        dbUserHealthAnalyze = dbUserHealthAnalyze.replace({'_p_appointmentId': r'^ScheduledAppointments\$'},
                                                          {'_p_appointmentId': ''}, regex=True)
        dbUserHealthAnalyze = dbUserHealthAnalyze.replace({'_p_support': r'^Support\$'}, {'_p_support': ''},
                                                          regex=True)
        dbUserHealthAnalyze = dbUserHealthAnalyze.replace({'_p_appointmentId': r'^ScheduledAppointments\$'},
                                                          {'_p_appointmentId': ''}, regex=True)
        dbUserHealthAnalyze = dbUserHealthAnalyze.replace({'_p_telephonecallId': r'^UserTelephoneCall\$'},
                                                          {'_p_telephonecallId': ''}, regex=True)

    else:
        dbUserHealthAnalyze = pd.DataFrame(tqdm(db[mongodb_collection].find(filtro, colunas),
                                                desc="Total itens recebidos:"))
        print(f'Dataset {mongodb_collection} Criado!')
    return dbUserHealthAnalyze


def gerar_tabela_user_health_medicine(filtro=None, colunas=None, mongodb_collection='UserHealthMedicine'):
    contar_itens_collection(filtro, mongodb_collection)
    if colunas is None:
        dbUserHealthMedicine = pd.DataFrame(tqdm(db[mongodb_collection].find(filtro, {'_id': 1,
                                                                                      '_created_at': 1,
                                                                                      '_p_corporation': 1,
                                                                                      '_p_user': 1,
                                                                                      'category': 1,
                                                                                      'code': 1,
                                                                                      'name': 1,
                                                                                      'type': 1,
                                                                                      'dosage': 1,
                                                                                      'dosageMeasure': 1,
                                                                                      'frequency': 1,
                                                                                      'frequencyTime': 1,
                                                                                      'orientation': 1,
                                                                                      '_updated_at': 1,
                                                                                      '_p_doctor': 1,
                                                                                      'dosageInformation': 1,
                                                                                      '_p_supportId': 1,
                                                                                      'cidCode': 1,
                                                                                      'cidDescription': 1,
                                                                                      'isContinuous': 1,
                                                                                      'isControlled': 1,
                                                                                      'via': 1,
                                                                                      '_p_support': 1,
                                                                                      '_p_appointmentId': 1,
                                                                                      '_p_telephonecallId': 1}),

                                                 desc="Total itens recebidos:"))
        print(f'Realizando tratamento do Dataset {mongodb_collection}!')
        dbUserHealthMedicine = dbUserHealthMedicine.replace({'_p_corporation': r'^Corporation\$'},
                                                            {'_p_corporation': ''}, regex=True)
        dbUserHealthMedicine = dbUserHealthMedicine.replace({'_p_user': r'^_User\$'}, {'_p_user': ''}, regex=True)
        dbUserHealthMedicine = dbUserHealthMedicine.replace({'_p_doctor': r'^Staff\$'}, {'_p_doctor': ''},regex=True)
        dbUserHealthMedicine = dbUserHealthMedicine.replace({'_p_supportId': r'^Support\$'}, {'_p_supportId': ''},
                                                            regex=True)
        dbUserHealthMedicine = dbUserHealthMedicine.replace({'_p_support': r'^Support\$'}, {'_p_support': ''},
                                                            regex=True)
        dbUserHealthMedicine = dbUserHealthMedicine.replace({'_p_appointmentId': r'^ScheduledAppointments\$'},
                                                            {'_p_appointmentId': ''}, regex=True)
        dbUserHealthMedicine = dbUserHealthMedicine.replace({'_p_telephonecallId': r'^UserTelephoneCall\$'},
                                                            {'_p_telephonecallId': ''}, regex=True)

    else:
        dbUserHealthMedicine = pd.DataFrame(tqdm(db[mongodb_collection].find(filtro, colunas),
                                                 desc="Total itens recebidos:"))
    print(f'Dataset {mongodb_collection} Criado!')
    return dbUserHealthMedicine


def gerar_tabela_user_illness_allergy(filtro=None, colunas=None, mongodb_collection='UserIllnessAllergy'):
    contar_itens_collection(filtro, mongodb_collection)
    if colunas is None:
        UserIllnessAllergy = pd.DataFrame(tqdm(db[mongodb_collection].find(filtro, {'_id': 1,
                                                                                    '_p_user': 1,
                                                                                    'name': 1,
                                                                                    'isDeleted': 1,
                                                                                    '_p_catalogIllnessAllergy': 1,
                                                                                    'code': 1,
                                                                                    '_created_at': 1,
                                                                                    '_updated_at': 1,
                                                                                    'type': 1,
                                                                                    'diagnosisDate': 1,
                                                                                    'lastDoctorVisit': 1,
                                                                                    '_p_createdBy': 1,
                                                                                    '_p_supportId': 1,
                                                                                    '_p_appointmentId': 1,
                                                                                    '_p_corporation': 1,
                                                                                    'note': 1}),
                                               desc="Total itens recebidos:"))
        print(f'Realizando tratamento do Dataset {mongodb_collection}!')
        UserIllnessAllergy = UserIllnessAllergy.replace({'_p_corporation': r'^Corporation\$'},
                                                            {'_p_corporation': ''}, regex=True)
        UserIllnessAllergy = UserIllnessAllergy.replace({'_p_user': r'^_User\$'}, {'_p_user': ''},regex=True)
        UserIllnessAllergy = UserIllnessAllergy.replace({'_p_createdBy': r'^Staff\$'}, {'_p_createdBy': ''},regex=True)
        UserIllnessAllergy = UserIllnessAllergy.replace({'_p_supportId': r'^Support\$'}, {'_p_supportId': ''},
                                                            regex=True)
        UserIllnessAllergy = UserIllnessAllergy.replace({'_p_appointmentId': r'^ScheduledAppointments\$'},
                                                            {'_p_appointmentId': ''}, regex=True)
        UserIllnessAllergy = UserIllnessAllergy.replace({'_p_catalogIllnessAllergy': r'^CatalogIllnessAllergy\$'},
                                                        {'_p_catalogIllnessAllergy': ''}, regex=True)
    else:
        dbUserHealthMedicine = pd.DataFrame(tqdm(db[mongodb_collection].find(filtro, colunas),
                                                 desc="Total itens recebidos:"))
    print(f'Dataset {mongodb_collection} Criado!')
    return UserIllnessAllergy


def gerar_tabela_user_indicator(filtro=None, colunas=None, mongodb_collection='UserIndicator'):
    contar_itens_collection(filtro, mongodb_collection)
    if colunas is None:
        dbUserIndicator = pd.DataFrame(tqdm(db['UserIndicator'].find(filtro, {'_id': 1,
                                                                              '_created_at': 1,
                                                                              'date': 1,
                                                                              '_p_createdBy': 1,
                                                                              '_p_doctorPatient': 1,
                                                                              '_p_user': 1,
                                                                              '_updated_at': 1,
                                                                              'examDate': 1,
                                                                              'indicators': 1,
                                                                              'isDeleted': 1,
                                                                              'interactionId': 1,
                                                                              '_p_userAnamnesis': 1,
                                                                              'type': 1,
                                                                              '_p_appointmentId': 1,
                                                                              '_p_supportId': 1}),
                                            desc="Total itens recebidos:"))
        print(f'Realizando tratamento do Dataset {mongodb_collection}!')

        if len(dbUserIndicator) > 0:
            dbUserIndicator = dbUserIndicator.explode('indicators')
            dfUserIndicator = dbUserIndicator['indicators'].apply(pd.Series)

            for column, i in dfUserIndicator.items():
                if column == 'type':
                    dfUserIndicator.drop(['type'], axis=1, inplace=True)
                    # print('type')
                elif column == 'date':
                    dfUserIndicator.drop(['date'], axis=1, inplace=True)
                # if column == 0:
                #     print(0)
                #     dfUserIndicator.drop(['0'], axis=1, inplace=True)


                UserIndicator = pd.concat([dbUserIndicator.drop(['indicators'], axis=1), dfUserIndicator], axis=1)

                UserIndicator = UserIndicator.replace({'_p_createdBy': r'^Staff\$'}, {'_p_createdBy': ''}, regex=True)
                UserIndicator = UserIndicator.replace({'_p_user': r'^_User\$'}, {'_p_user': ''}, regex=True)
                UserIndicator = UserIndicator.replace({'_p_doctorPatient': r'^DoctorPatient\$'},
                                                      {'_p_doctorPatient': ''}, regex=True)
                UserIndicator = UserIndicator.replace({'_p_appointmentId': r'^ScheduledAppointments\$'},
                                                          {'_p_appointmentId': ''}, regex=True)
                UserIndicator = UserIndicator.replace({'_p_supportId': r'^Support\$'}, {'_p_supportId': ''}, regex=True)
                UserIndicator = UserIndicator.replace({'_p_userAnamnesis': r'^UserAnamnesis\$'},
                                                      {'_p_userAnamnesis': ''}, regex=True)
                UserIndicator.drop(columns=['meameasurement',
                                            'measure',
                                            'isHide',
                                            'prePrandial',
                                            'values',
                                            'postPrandial',
                                            'note'], inplace=True)
        else:
            UserIndicator = pd.DataFrame()

        print(f'Dataset {mongodb_collection} Criado!')
    else:
        UserIndicator = pd.DataFrame(tqdm(db['UserIndicator'].find(filtro, colunas)))
        print(f'Dataset {mongodb_collection} Criado!')

    return UserIndicator


def gerar_tabela_user_anamnesis(filtro=None, colunas=None, mongodb_collection='UserAnamnesis'):
    contar_itens_collection(filtro, mongodb_collection)
    if colunas is None:
        dbUserAnamnesis = pd.DataFrame(tqdm(db[mongodb_collection].find(filtro, {'_id': 1,
                                                                                 '_created_at': 1,
                                                                                 '_p_user': 1,
                                                                                 '_updated_at': 1,
                                                                                 "answers": 1,
                                                                                 'care_plan_file': 1,
                                                                                 'anamnesisCorporation': 1,
                                                                                 "sequence": 1,
                                                                                 'date_finished': 1,
                                                                                 'date_start': 1,
                                                                                 "is_deleted": 1,
                                                                                 'is_finished': 1,
                                                                                 'healthProfile': 1,
                                                                                 '_p_created_by': 1,
                                                                                 'group': 1}),
                                            desc="Total itens recebidos:"))

        print(f'Realizando tratamento do Dataset {mongodb_collection}!')
        dbUserAnamnesis = dbUserAnamnesis.replace({'_p_user': r'^_User\$'}, {'_p_user': ''}, regex=True)
        dbUserAnamnesis = dbUserAnamnesis.replace({'_p_created_by': r'^Staff\$'}, {'_p_created_by': ''}, regex=True)
        print(f'Dataset {mongodb_collection} Criado!')
    else:
        print('Nesta Collection ainda não é possivel escolher as colunas')
    return dbUserAnamnesis


def gerar_tabela_scheduled_staff(filtro=None, colunas=None, mongodb_collection='ScheduledStaff'):
    contar_itens_collection(filtro, mongodb_collection)
    if colunas is None:
        dbScheduledStaff = pd.DataFrame(tqdm(db[mongodb_collection].find(filtro, {'_id': 1,
                                                                                  '_created_at': 1,
                                                                                  '_updated_at': 1,
                                                                                  '_p_user': 1,
                                                                                  '_p_staff': 1,
                                                                                  'corporation': 1,
                                                                                  'is_deleted': 1,
                                                                                  'isScheduling': 1,
                                                                                  'isBlocked': 1,
                                                                                  'speciality': 1,
                                                                                  'job': 1}),
                                             desc="Total itens recebidos:"))

        print(f'Realizando tratamento do Dataset {mongodb_collection}!')
        dbScheduledStaff = dbScheduledStaff.replace({'_p_user': r'^_User\$'}, {'_p_user': ''}, regex=True)
        dbScheduledStaff = dbScheduledStaff.replace({'_p_staff': r'^Staff\$'},{'_p_staff': ''},regex=True)
        dbScheduledStaff = dbScheduledStaff.replace({'_p_corporation': r'^Corporation\$'}, {'_p_corporation': ''},
                                                    regex=True)
        print(f'Dataset {mongodb_collection} Criado!')
    else:
        print('Nesta Collection ainda não é possivel escolher as colunas')
    return dbScheduledStaff


def gerar_tabela_specielities(filtro=None, colunas=None, mongodb_collection='Specialities'):
    contar_itens_collection(filtro, mongodb_collection)
    if colunas is None:
        dbspecialities = pd.DataFrame(tqdm(db[mongodb_collection].find(filtro, {'_id': 1,
                                                                                '_created_at': 1,
                                                                                '_updated_at': 1,
                                                                                'accessRoles': 1,
                                                                                'corporations': 1,
                                                                                'interval': 1,
                                                                                'name': 1,
                                                                                'cbo': 1,
                                                                                'journeyLabel': 1,
                                                                                'soapType': 1,
                                                                                'journeyCode': 1}),
                                           desc="Total itens recebidos:"))

        print(f'Realizando tratamento do Dataset {mongodb_collection}!')
        print(f'Dataset {mongodb_collection} Criado!')
    else:
        print('Nesta Collection ainda não é possivel escolher as colunas')
    return dbspecialities
