from app.models.models import Tour
from datetime import datetime, timedelta

def seed_tours(db):
    # Очищаем существующие данные
    db.query(Tour).delete()
    
    # Создаем тестовые туры
    tours = [
        Tour(
            title="Гастрономический тур по Италии",
            description="Откройте для себя вкусы Италии: от пасты до пиццы, от вина до мороженого. Посетите лучшие рестораны и винодельни.",
            price=2500.0,
            duration=7,
            image_url="https://example.com/italy-food.jpg",
            location="Италия",
            rating=4.8,
            max_participants=12,
            available_spots=8,
            is_hot=True,
            departure_date=datetime.now() + timedelta(days=30),
            return_date=datetime.now() + timedelta(days=37),
            available_dates=[
                datetime.now() + timedelta(days=30),
                datetime.now() + timedelta(days=60),
                datetime.now() + timedelta(days=90)
            ]
        ),
        Tour(
            title="Японская кулинарная экспедиция",
            description="Погрузитесь в мир японской кухни: суши, сашими, рамен и многое другое. Мастер-классы от лучших шеф-поваров.",
            price=3000.0,
            duration=10,
            image_url="https://example.com/japan-food.jpg",
            location="Япония",
            rating=4.9,
            max_participants=10,
            available_spots=5,
            is_hot=True,
            departure_date=datetime.now() + timedelta(days=45),
            return_date=datetime.now() + timedelta(days=55),
            available_dates=[
                datetime.now() + timedelta(days=45),
                datetime.now() + timedelta(days=75),
                datetime.now() + timedelta(days=105)
            ]
        ),
        Tour(
            title="Французская кулинарная школа",
            description="Изучите основы французской кухни в лучших кулинарных школах Парижа. Круассаны, паштеты, соусы и многое другое.",
            price=2800.0,
            duration=8,
            image_url="https://example.com/france-food.jpg",
            location="Франция",
            rating=4.7,
            max_participants=15,
            available_spots=12,
            is_hot=False,
            departure_date=datetime.now() + timedelta(days=60),
            return_date=datetime.now() + timedelta(days=68),
            available_dates=[
                datetime.now() + timedelta(days=60),
                datetime.now() + timedelta(days=90),
                datetime.now() + timedelta(days=120)
            ]
        )
    ]
    
    for tour in tours:
        db.add(tour)
    
    db.commit() 