
import os
from werkzeug.utils import secure_filename
from flask import Flask, request, render_template, redirect, flash,send_file,url_for
from sqlalchemy import create_engine

app = Flask(__name__)

app.debug = True

dbuser = 'root'
dbhost = 'localhost'
dbpass = 'strepto._2coccus'
dbname = 'phonebook'
engine = create_engine('mysql://{0}:{1}@{2}/{3}'.format(dbuser, dbpass, dbhost, dbname))

from sqlalchemy.orm import declarative_base

Base = declarative_base()

from sqlalchemy import Column, Integer, String, ForeignKey


class Cities(Base):
    __tablename__ = 'cities'
    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    code = Column(String, nullable=False, unique=True)


class Contacts(Base):
    __tablename__ = 'contacts'
    id = Column(Integer, primary_key=True)
    first_name = Column(String, nullable=False)
    last_name = Column(String, nullable=False)
    city_id = Column(Integer, ForeignKey('cities.id'))
    phone = Column(String, nullable=False)
    image = Column(String)


class Numbers(Base):
    __tablename__ = 'numbers'
    id = Column(Integer, primary_key=True)
    contact_id = Column(Integer, nullable=False)
    number = Column(String)


class Users(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True)
    username = Column(String, nullable=False)
    password = Column(String, nullable=False)
    user_admin = Column(String, nullable=False)


Base.metadata.create_all(engine)
from sqlalchemy.orm import sessionmaker

session = sessionmaker(bind=engine)
db = session()

UPLOAD_FOLDER = 'C:/Users/pc sys/Desktop/webserver_phonebook/my_env/static/uploads/'
app.secret_key = "secret key"
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

id_holder = []
phone_id = []
id_holder_second = []


def validate(e, p, ee, pp):
    records = db.query(Users)
    for record in records:
        if record.username == e:
            ee = False
            flash(f'{e} is already registered!', "alert")
            break
        if ee:
            if record.password == p:
                pp = False
                flash(f'{p} is taken !', "alert")
                break
    if ee == True and pp == True:
        return True


def city_validation(city, code, ee, pp):
    records = db.query(Cities)
    for record in records:
        if record.name == city:
            ee = False
            flash(f'{city} already exists!', "alert")
            break
        if ee:
            if record.code == code:
                pp = False
                flash(f'{code} already exists!', "alert")
                break
    if ee == True and pp == True:
        return True







@app.route('/')
def hello_world():
    return "hello world :')"


@app.route('/index', methods=['post', 'get'])
def index():
    if request.method == 'POST':
        records = db.query(Users)
        e = request.form['email']
        p = request.form['password']
        ee = False
        pp = False
        n = []
        if e == "":
            flash('Please input an email!', "alert")
            return render_template('index.html')
        if p == "":
            flash('Please input a password!', "alert")
            return render_template('index.html')
        for record in records:
            if record.username == e:
                ee = True

            if record.password == p:
                pp = True
                n.clear()
                n.append(record.user_admin)

                break

        if pp == False and ee == False:
            flash('This Account Is Not Registered', "alert")
            return render_template('index.html')
        if pp == False:
            flash('Password Is Incorrect', "alert")
            return render_template('index.html')
        if ee == False:
            flash('Email Is Incorrect', "alert")
            return render_template('index.html')
        if ee == True and pp == True:
            if n[0] == '1':
                flash(f'Welcome {e},You Are Successfully Logged In ', "alert")
                data = db.query(Contacts).order_by(Contacts.first_name)
                return render_template('Contacts.html', data=data)
            if n[0] == '2':
                flash(f'Welcome {e},You Are Successfully Logged In ', "alert")
                data = db.query(Cities).order_by(Cities.name)
                return render_template('city.html', data=data)


    else:

        return render_template('index.html')


@app.route('/signup', methods=['post', 'get'])
def signup():
    if request.method == 'POST':

        e = request.form['email']
        p = request.form['password']
        ee = True
        pp = True
        if e == "":
            flash('Please input an email!', "alert")
            return render_template('signup.html')
        if p == "":
            flash('Please input a password!', "alert")
            return render_template('signup.html')

        if validate(e, p, ee, pp):
            user = Users(username=e, password=p, user_admin="1")
            db.add(user)
            db.commit()

            flash(f'Welcome {e},You Are Successfully Signed Up ', "alert")
            return render_template('Contacts.html')

        return render_template('signup.html')
    else:

        return render_template('signup.html')


@app.route('/admin', methods=['post', 'get'])
def admin():
    if request.method == 'POST':

        e = request.form['email']
        p = request.form['password']
        ee = True
        pp = True
        if e == "":
            flash('Please input an email!', "alert")
            return render_template("admin.html")
        if p == "":
            flash('Please input a password!', "alert")
            return render_template("admin.html")
        if validate(e, p, ee, pp):
            user = Users(username=e, password=p, user_admin="2")
            db.add(user)
            db.commit()
            flash(f'Congratulations! {e},You are successfully signed up', "alert")
            data = db.query(Cities).order_by(Cities.name)
            return render_template('city.html', data=data)

        return render_template("admin.html")
    else:

        return render_template('admin.html')


@app.route('/add', methods=['post', 'get'])
def add():
    if request.method == 'POST':

        city = request.form['city']
        code = request.form['code']
        ee = True
        pp = True
        if city == "":
            flash('Please input city!', "alert")
            return render_template("add.html")
        if code == "":
            flash('Please input code!', "alert")
            return render_template("add.html")

        if city_validation(city, code, ee, pp):
            city_r = Cities(name=city, code=code)
            db.add(city_r)
            db.commit()
            flash(f'{city} was successfully added!', "alert")
            data = db.query(Cities).order_by(Cities.name)
            return render_template('city.html', data=data)

        return render_template('add.html')
    else:

        return render_template('add.html')


@app.route('/city', methods=['post', 'get'])
def city():
    if request.method == 'POST':
        info = request.form['search']
        if info != " ":
            data = db.query(Cities).filter(Cities.name.like('%' + info + '%')).order_by(Cities.name)
            return render_template('city.html', data=data)
        data = db.query(Cities).order_by(Cities.name)
        return render_template('city.html', data=data)
    else:

        return render_template('city.html')


@app.route('/intermediary/<int:id>')
def intermediary(id):
    records = db.query(Cities)
    for record in records:
        if record.id == id:
            city = record.name
            code = record.code
            id_holder.clear()
            id_holder.append(id)

            return render_template('edit.html', city=city, code=code)


@app.route('/edit', methods=['post', 'get'])
def edit():
    if request.method == 'POST':
        city = request.form['city']
        code = request.form['code']
        if city == "":
            flash('Please input city!', "alert")
            return render_template("edit.html")

        if code == "":
            flash('Please input code!', "alert")
            return render_template("edit.html")

        records = db.query(Cities)
        for record in records:

            if record.id == id_holder[0]:
                pre_city = record.name
                pre_code = record.code

                for record in records:
                    if city != pre_city and city == record.name:
                        flash(f"{city} Already Exists!!!", "alert")
                        return render_template('edit.html')

                    if code != pre_code and code == record.code:
                        flash(f"City code {code}  Already Exists!!!", "alert")
                        return render_template('edit.html')

        for record in records:
            if record.id == id_holder[0]:
                record.name = city
                record.code = code
                db.commit()

                flash(f'You successfully changed Your city name and city code to= {city} and {code} !',
                      "alert")
                data = db.query(Cities).order_by(Cities.name)
                return render_template('city.html', data=data)
    else:
        return render_template('edit.html')


@app.route('/delete/<int:id>')
def delete(id):
    records = db.query(Cities)
    for record in records:
        if record.id == id:
            db.delete(record)
            db.commit()
            data = db.query(Cities).order_by(Cities.name)
            flash(f'{record.name} was successfully deleted!', "alert")
            return render_template("city.html", data=data)


@app.route('/addintermediary')
def addintermediary():
    data = db.query(Cities).order_by(Cities.name)

    return render_template('addcontact.html', data=data)


@app.route('/addcontact', methods=['post', 'get'])
def addcontact():
    if request.method == 'POST':

        name = request.form['name']
        last = request.form['last']
        phone_1 = request.form['phone_1']
        phone_2 = request.form['phone_2']
        phone_3 = request.form['phone_3']
        p_1 = []
        p_1.clear()
        p_1.append(phone_1)
        p_2 = []
        p_2.clear()
        p_2.append(phone_2)
        p_3 = []
        p_3.clear()
        p_3.append(phone_3)
        se = []
        se.clear()
        select_value = request.form['select1']
        se.append(select_value)
        file = request.files['file']

        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))




        p = [p_1[0], p_2[0], p_3[0]]

        if name == "":
            flash('Please input first name!', "alert")
            return redirect("addintermediary")
        if last == "":
            flash('Please input last name!', "alert")
            return redirect("addintermediary")
        if phone_1 == "":
            flash('Please input phone number!', "alert")
            return redirect("addintermediary")
        if se == [' ']:
            flash('Please select a city!', "alert")
            return redirect("addintermediary")
        records = db.query(Contacts)
        for record in records:
            if record.first_name + record.last_name == name + last:
                flash(f'{record.first_name + " " + record.last_name} already exists!', "alert")
                return redirect("addintermediary")
            numb = db.query(Numbers)

            for num in numb:
                for i in range(3):
                    if num.number != "09XXXXXXXXX":
                        if num.number == p[i]:
                            flash(f'This phone number: {p[i]} already exists!', "alert")
                            return redirect("addintermediary")


            if record.image == filename:
                    flash(f'This picture already exists!', "alert")
                    return redirect("addintermediary")
        phone_id.clear()
        phone_id.append(1)
        for record in records:
            id = record.id
            id += 1
            phone_id.clear()
            phone_id.append(id)

        for i in range(3):
            if p[i] != '':

                db.query(Numbers)
                numbersss = Numbers(contact_id=phone_id[0], number=p[i])
                db.add(numbersss)
            else:

                db.query(Numbers)
                numbersss = Numbers(contact_id=phone_id[0], number="09XXXXXXXXX")
                db.add(numbersss)
        db.query(Contacts)
        new_contacat = Contacts(first_name=name, last_name=last, city_id=se[0], phone=phone_id[0], image=filename)
        db.add(new_contacat)
        db.commit()
        flash(f'Youre contact: {name + last} was successfully saved!', "alert")
        data = db.query(Contacts).order_by(Contacts.first_name)
        return render_template('contacts.html', data=data)


    else:
        redirect("addintermediary")


@app.route('/contacts', methods=['post', 'get'])
def contacts():
    if request.method == 'POST':
        info = request.form['search']
        if info != " ":
            data = db.query(Contacts).filter(Contacts.first_name.like('%' + info + '%')).order_by(Contacts.first_name)
            return render_template('contacts.html', data=data)
    else:

        return render_template('contacts.html')


@app.route('/deletecontact/<int:id>')
def deletecontact(id):
    records = db.query(Contacts)
    for record in records:
        if record.id == id:
            numbs = db.query(Numbers)
            for num in numbs:
                if record.phone == num.contact_id:
                    db.delete(num)
                    db.commit()
            db.delete(record)
            db.commit()
            data = db.query(Contacts).order_by(Contacts.first_name)
            flash(f'{record.first_name + " " + record.last_name} was successfully deleted!', "alert")
            return render_template("contacts.html", data=data)


@app.route('/intermediaryeditcontact/<int:id>')
def intermediaryeditcontact(id):
    records = db.query(Contacts)
    for record in records:
        if record.id == id:
            numbs = db.query(Numbers)
            number = []
            number.clear()
            for num in numbs:
                if num.contact_id == record.phone:
                    number.append(num.number)
            citys = db.query(Cities)
            for city in citys:
                if city.id == record.city_id:
                    sel_city = city.name

            number_1 = number[0]
            number_2 = number[1]
            number_3 = number[2]
            name = record.first_name
            last = record.last_name
            img = record.image
            id_holder.clear()
            id_holder.append(id)

            return render_template('editcontact.html', name=name, last=last, number_1=number_1, number_2=number_2,
                                   number_3=number_3, sel_city=sel_city, citys=citys, img=img)


@app.route('/editcontact', methods=['post', 'get'])
def editcontact():
    if request.method == 'POST':
        id_holder_second.clear()
        id_holder_second.append(id_holder[0])
        name = request.form['name']
        last = request.form['last']
        phone_1 = request.form['phone_1']
        phone_2 = request.form['phone_2']
        phone_3 = request.form['phone_3']
        p_1 = []
        p_1.clear()
        p_1.append(phone_1)
        p_2 = []
        p_2.clear()
        p_2.append(phone_2)
        p_3 = []
        p_3.clear()
        p_3.append(phone_3)
        se = []
        se.clear()
        select_value = request.form['select1']
        se.append(select_value)
        file = request.files['file']

        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))

        p = [p_1[0], p_2[0], p_3[0]]

        if name == "":
            flash('Please input first name!', "alert")
            return redirect('sh')
        if last == "":
            flash('Please input last name!', "alert")
            return redirect('sh')
        if phone_1 == "":
            flash('Please input phone number!', "alert")
            return redirect('sh')
        if se == [' ']:
            flash('Please select a city!', "alert")
            return redirect('sh')

        records = db.query(Contacts)
        for record in records:
            if record.id == id_holder[0]:
                nums = db.query(Numbers)
                number = []
                number.clear()
                for num in nums:
                    if num.contact_id == record.phone:
                        number.append(num.number)

                pre_number_1 = number[0]
                pre_number_2 = number[1]
                pre_number_3 = number[2]

                pre_name = record.first_name
                pre_last = record.last_name
                pre_image = record.image

                for record in records:
                    if name != pre_name and last != pre_last and name == record.first_name and last == record.last_name:
                        flash(f"{name + ' ' + last} Already Exists!!!", "alert")
                        return redirect('sh')

                    if filename != pre_image and filename == record.image:
                        flash(f"This Picture Already Exists!!!", "alert")
                        return redirect('sh')
                    nums = db.query(Numbers)
                    pre = [pre_number_1, pre_number_2, pre_number_3]
                    for i in range(3):
                        for num in nums:
                            if p[i] != "09XXXXXXXXX" and p[i] != pre[i] and p[i] == num.number:
                                flash(f"This Number: {p[i]} Already Exists!!!", "alert")
                                return redirect('sh')

        records = db.query(Contacts)
        for record in records:
            if record.id == id_holder[0]:
                record.first_name = name
                record.last_name = last
                record.city_id = se[0]
                nums = db.query(Numbers)
                i = 0
                for num in nums:
                    if record.phone == num.contact_id:
                        if p[i]!="":
                          num.number = p[i]
                        else:
                            num.number = "09XXXXXXXXX"

                        i += 1
                record.image = filename
                db.commit()
                flash(f'You successfully have changed Your contact!',
                      "alert")
                data = db.query(Contacts).order_by(Contacts.first_name)
                return render_template('contacts.html', data=data)
    else:
        return render_template('editcontact.html')


@app.route('/sh')
def sh():
    records = db.query(Contacts)
    for record in records:
        if record.id == id_holder_second[0]:
            numbs = db.query(Numbers)
            number = []
            number.clear()
            for num in numbs:
                if num.contact_id == record.phone:
                    number.append(num.number)
            citys = db.query(Cities)
            for city in citys:
                if city.id == record.city_id:
                    sel_city = city.name

            number_1 = number[0]
            number_2 = number[1]
            number_3 = number[2]
            name = record.first_name
            last = record.last_name
            img = record.image
            id_holder.clear()
            id_holder.append(id_holder_second[0])

            return render_template('editcontact.html', name=name, last=last, number_1=number_1, number_2=number_2,
                                   number_3=number_3, sel_city=sel_city, citys=citys, img=img)

@app.route('/view/<int:id>')
def view(id):
    records = db.query(Contacts)
    for record in records:
        if record.id == id:
            numbs = db.query(Numbers)
            number = []
            number.clear()
            for num in numbs:
                if num.contact_id == record.phone:
                    number.append(num.number)
            citys = db.query(Cities)
            for city in citys:
                if city.id == record.city_id:
                    sel_city = city.name
                    code = city.code


            number_1 = number[0]
            if number_1=="09XXXXXXXXX":
                number_1=" None Existent"
            number_2 = number[1]
            if number_2=="09XXXXXXXXX":
                number_2=" None Existent "
            number_3 = number[2]
            if number_3=="09XXXXXXXXX":
                number_3=" None Existent "

            name = record.first_name
            last = record.last_name
            img = record.image

            id_holder.clear()
            id_holder.append(id)



            return render_template('view.html', name=name, last=last, number_1=number_1, number_2=number_2,
                                   number_3=number_3, sel_city=sel_city, img=img , code=code)


@app.route('/c', methods=['post', 'get'])
def c():
    if request.method == 'POST':

            data = db.query(Contacts).order_by(Contacts.first_name)
            return render_template('contacts.html', data=data)
    else:

        return render_template('contacts.html')


@app.route('/display/<filename>')
def display_image(filename):
    #print('display_image filename: ' + filename)
    return redirect(url_for('static', filename='uploads/' + filename), code=301)


if __name__ == __name__:
    app.secret_key = b'_5#y2L"F4Q8z/'
    app.run()
