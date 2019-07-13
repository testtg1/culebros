from app import db

Model = db.Model
Column = db.Column
String = db.String
Integer = db.Integer

session = db.session


class Users(Model):
    __tablename__ = 'users'

    id = Column(Integer, primary_key = True)
    balance = Column(Integer)

    def get(id):
        return Users.query.get(id)

    
    def new(id):
        user = Users.get(id)
        if user:
            return None
        
        if not user:
            user = Users(id = id, balance = 0)
            session.add(user)
            session.commit()
            return True


class Referals(Model):
    __tablename__ = 'referals'

    owner_id = Column(Integer)
    referal_id = Column(Integer)

    rid = Column(Integer, primary_key = True)

    def get_by_owner(owner_id):
        return Referals.query.filter_by(owner_id = int(owner_id)).all()
    
    def get_owner(referal_id):
        return Referals.query.filter_by(referal_id = int(referal_id)).first()

    
    def new(owner_id, referal_id):
        referal = Referals.get_owner(referal_id)
        if referal:
            return None
        
        if not referal:
            new_referal = Referals(owner_id = owner_id, referal_id = referal_id)
            session.add(new_referal)
            session.commit()
            return new_referal


class SportStats(Model):
    __tablename__ = 'sportstats'

    category = Column(String)
    name = Column(String)
    link = Column(String)

    id = Column(Integer, primary_key = True)


class Subscribers(Model):
    __tablename__ = 'subscribers'

    id = Column(Integer, primary_key = True)
    payment_date = Column(Integer)
    date_to_payment = Column(Integer)



class Payments(Model):
    __tablename__ = 'payments'

    id = Column(Integer)
    amount = Column(Integer)
    date = Column(Integer)
    tariff_id = Column(Integer, nullable=True)

    payment_id = Column(Integer, primary_key = True)

    def new(user_id, amount, date, tariff_id):
        payment = Payments(
            id = int(user_id),
            amount = int(amount), 
            date = int(date),
            tariff_id = int(tariff_id)
        )
        
        session.add(payment)
        session.commit()
        return payment
        



class NewsLetters(Model):
    __tablename__ = 'newsletters'

    sport_category = Column(String)
    text = Column(String)

    nlid = Column(Integer, primary_key = True)



class Subscribes(Model):
    __tablename__ = 'subscribes'

    name = Column(String)
    price = Column(String)
    time = Column(Integer)
    to_ref_money = Column(Integer)

    sid = Column(Integer, primary_key = True)