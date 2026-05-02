from database import init_db, get_session
from models import Product

def seed():
    init_db()
    session = get_session()

    if session.query(Product).count() > 0:
        print('Database already seeded.')
        session.close()
        return

    products = [
        Product(product_id='101', name='Classic Burger',      stock=15, price=149),
        Product(product_id='102', name='Double Stack',        stock=8,  price=189),
        Product(product_id='103', name='Spicy Burger',        stock=6,  price=169),
        Product(product_id='104', name='Mushroom Swiss',      stock=0,  price=179),
        Product(product_id='201', name='Chicken Fillet',      stock=20, price=159),
        Product(product_id='202', name='Spicy Chicken Wings', stock=12, price=199),
        Product(product_id='203', name='Chicken Nuggets 6pc', stock=4,  price=129),
        Product(product_id='301', name='Large Fries',         stock=30, price=79),
        Product(product_id='302', name='Onion Rings',         stock=10, price=89),
        Product(product_id='303', name='Coleslaw',            stock=0,  price=59),
        Product(product_id='401', name='Coke Float',          stock=25, price=69),
        Product(product_id='402', name='Mango Shake',         stock=7,  price=99),
        Product(product_id='403', name='Iced Coffee',         stock=15, price=89),
        Product(product_id='501', name='Soft Serve Cone',     stock=20, price=39),
        Product(product_id='502', name='Hot Fudge Sundae',    stock=9,  price=69),
        Product(product_id='503', name='Apple Pie',           stock=0,  price=49),
        Product(product_id='601', name='Big Meal Deal',       stock=10, price=279),
        Product(product_id='602', name='Chicken Combo',       stock=5,  price=299),
    ]

    session.add_all(products)
    session.commit()
    session.close()
    print('Products seeded successfully.')

if __name__ == '__main__':
    seed()