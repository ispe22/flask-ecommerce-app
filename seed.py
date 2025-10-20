from app import db
from models import Product

def seed_data():
    #db.drop_all()
    #db.create_all()
    print("Seeding database with initial products...")
    product_1 = Product(name='Cosmic Harmony AI Painting', description='This enchanting painting captures a moment of profound wonder in a mystical landscape. A lone figure stands, arms outstretched, beneath a breathtaking spiral galaxy that unfurls across the twilight sky. Lush, gnarled trees with roots like ancient guardians frame a cascading waterfall that feeds into a winding river. Towering mountains recede into the distance, all bathed in the soft glow of a setting sun and the vibrant hues of a cosmic spectacle.', price=15.93, stock_quantity=100, image_url='/static/images/ai_painting_1.png')
    product_2 = Product(name='Neon Metropolis Dragon AI Painting', description='This dynamic artwork plunges us into a vibrant, rain-slicked cyberpunk city at night. Towering skyscrapers adorned with glowing neon signs in Japanese characters illuminate the bustling street below, where citizens navigate under their umbrellas. Above it all, a majestic, ethereal blue dragon, imbued with an otherworldly light, hovers ominously, overseeing the futuristic urban sprawl. Flying vehicles add to the high-tech, yet mysterious atmosphere.', price=7.96, stock_quantity=200, image_url='/static/images/ai_painting_2.png')
    product_3 = Product(name='Atlantis Voyager AI Painting', description='Dive into the depths with this fantastical underwater scene. A steampunk-inspired submarine, glowing with warm light, navigates through the ruins of an ancient, submerged city, reminiscent of Atlantis. Vibrant coral and marine flora adorn the decaying structures. Schools of fish swim among the ruins, while luminous jellyfish drift gracefully above, their tendrils trailing in the gentle currents, adding to the otherworldly charm of this deep-sea adventure.', price=3.98, stock_quantity=300, image_url='/static/images/ai_painting_3.png')
    
    db.session.add_all([product_1, product_2, product_3])
    db.session.commit()
    print("Seed complete.")
