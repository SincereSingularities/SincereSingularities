from dataclasses import dataclass


@dataclass
class EmbeddableNoiseFoods:
    """EmbeddableNoiseFoods"""
    starters: list[str]
    main: list[str]
    desserts: list[str]
    drinks: list[str]

@dataclass
class EmbeddableNoise:
    """EmbeddableNoise"""
    addresses: list[str]
    foods: EmbeddableNoiseFoods
    times: list[str]
    restaurants: list[str]

@dataclass
class NoiseData:
    """NoiseData"""
    noise: list[str]
    relevant_noise: list[str]
    embeddable_noise: EmbeddableNoise

NOISE = NoiseData(
    noise=[
        "It's such a sunny day today, perfect for a walk in the park.",
        "Yesterday was unbelievable with how much it rained, flooding the streets.",
        "The sky looks so clear and blue, not a cloud in sight.",
        "This morning, I had a great time at the park watching the ducks.",
        "My cat knocked over my plant again, creating quite the mess.",
        "Finally finished reading that book I've been working on for weeks.",
        "Dinner last night was fantastic, especially the dessert.",
        "I can't wait for the weekend to relax and maybe go hiking.",
        "Traffic was terrible this morning, making me late for work.",
        "Planning to bake cookies later with a new recipe I found.",
        "Have you seen the latest movie that's causing such a buzz?",
        "My dog loves playing fetch in the yard, never gets tired.",
        "Groceries are on my list after work, running low on essentials.",
        "The sunset yesterday was absolutely beautiful, with vibrant colors.",
        "Cleaned my entire house today, feels so refreshing now.",
        "Thinking about redecorating my living room, maybe new curtains.",
        "The flowers in my garden are blooming nicely, adding color to the yard.",
        "Spent the afternoon organizing my closet, found some old treasures.",
        "Tried a new recipe for lunch today, it was surprisingly good.",
        "Can't find my keys anywhere, looked in all the usual spots.",
        "Neighbors are having a barbecue this weekend, invited the whole block.",
        "Need to take my car for a service, it's been making weird noises.",
        "Power went out for a couple of hours, had to use candles.",
        "Learning to play the guitar, slowly but surely improving.",
        "Had a lovely walk by the beach, the sound of waves was soothing.",
        "Friend is coming over for coffee tomorrow, can't wait to catch up.",
        "Watering the plants before I leave, they look a bit dry.",
        "The birds are singing so loudly today, feels like a symphony.",
        "Saw a beautiful rainbow after the rain, it was magical.",
        "Need to finish my project by the end of the week, deadlines are tight.",
        "The coffee shop on the corner makes the best lattes, a must-try.",
        "Love the smell of fresh laundry, so clean and crisp.",
        "Had the most delicious breakfast this morning, pancakes and syrup.",
        "Replace the light bulb in the kitchen, it's been flickering.",
        "Found a great deal on a new laptop, couldn't resist buying it.",
        "The air feels so fresh after the rain, perfect for a run.",
        "Planning a surprise party for my friend, hope she loves it.",
        "Just bought a new set of paints, excited to start a new project.",
        "Weather forecast says it will be sunny all week, time for outdoor fun.",
        "Love listening to music while I cook, makes it more enjoyable.",
        "Can't believe it's already July, time flies so fast.",
        "My plants are growing so fast, need to repot some of them.",
        "Book a dentist appointment, it's been a while since my last check-up.",
        "Spent the day hiking in the mountains, the views were breathtaking.",
        "Tried yoga for the first time today, felt incredibly relaxing.",
        "The stars are so bright tonight, perfect for stargazing.",
        "Finally organized my desk, now it looks neat and tidy.",
        "Planning to visit my grandparents this weekend, always a pleasure.",
        "Love the sound of rain on the roof, so calming.",
        "Need to buy a new phone charger, mine is fraying.",
        "Had a picnic in the park today, the weather was perfect.",
        "The autumn leaves are so beautiful, love the vibrant colors.",
        "Vacuum the living room, it's starting to look a bit dusty.",
        "Thinking about getting a new pet, maybe a rabbit.",
        "Found a new favorite TV show, binge-watched the first season.",
        "The sunrise was stunning this morning, worth waking up early for.",
        "Do the dishes before bed, don't want a messy kitchen in the morning.",
        "Spent the evening reading a great book, couldn't put it down.",
        "Neighborhood kids are playing outside, their laughter is contagious.",
        "Need to clean out the garage, it's getting cluttered.",
        "Love the feeling of fresh sheets on the bed, so comfortable.",
        "Went for a bike ride along the river, the scenery was beautiful.",
        "Can't wait to try the new restaurant in town, heard great reviews.",
        "Bought a new rug for the living room, adds a nice touch.",
        "Looking forward to the holiday season, always so festive.",
        "The flowers smell amazing in the garden, such a pleasant aroma.",
        "Had a relaxing bath after a long day, felt rejuvenating.",
        "Found my old photo albums in the attic, such memories.",
        "Love making smoothies for breakfast, so refreshing and healthy.",
        "Wash the car this weekend, it's covered in dust.",
        "Spent the afternoon painting, lost track of time.",
        "The dog park was full of happy dogs, running and playing.",
        "Buy a new alarm clock, mine stopped working.",
        "Love watching the sunset from my balcony, a daily highlight.",
        "Went to the farmers' market this morning, got fresh produce.",
        "The moon is so bright tonight, lighting up the whole yard.",
        "Fix the leaky faucet in the bathroom, the dripping is annoying.",
        "Had a fun game night with friends, lots of laughs.",
        "Love the scent of fresh flowers, brightens my day.",
        "Found a great recipe for dinner, can't wait to try it.",
        "Take out the trash, the bin is overflowing.",
        "The backyard is a great place to relax, especially in the evening.",
        "Love the taste of fresh fruit, so juicy and sweet.",
        "Organize my bookshelf, it's starting to overflow.",
        "Went for a run in the park, the fresh air was invigorating.",
        "Bought a new pillow for my bed, sleep should be even better now.",
        "Planning a road trip next month, excited for the adventure.",
        "The streetlights are glowing softly, creating a serene atmosphere.",
        "Pick up my dry cleaning, need my favorite dress for an event.",
        "Love the feeling of the sun on my skin, so warm and soothing.",
        "Had a delicious cup of tea this morning, perfect start to the day.",
        "Mow the lawn this weekend, it's getting too long.",
        "Spent the day at the beach, the sound of waves was relaxing.",
        "Love the sound of birds in the morning, nature's alarm clock.",
        "Get a haircut soon, my hair is getting too long.",
        "Had a great workout at the gym, feeling energized.",
        "The sky is so clear and beautiful, perfect for photography.",
        "Send some emails, catching up on correspondence.",
        "Went for a drive in the countryside, the views were stunning.",
        "Love the color of the leaves in fall, such a beautiful transformation.",
        "Replace the batteries in the remote, it's not working properly.",
        "Had a productive day at work, accomplished a lot.",
        "Love trying new recipes, cooking is so much fun.",
        "Update my calendar, lots of events coming up.",
        "The garden looks so green after the rain, so refreshing.",
        "Had a relaxing afternoon nap, felt so good.",
        "Buy some new clothes, need a wardrobe update.",
        "Love the quietness of the morning, so peaceful.",
        "Had a fun time at the zoo, the animals were fascinating.",
        "Plan my next vacation, thinking of going somewhere tropical.",
        "Love the feeling of clean floors, makes the house feel fresh.",
        "Had a nice chat with my neighbor, they're really friendly.",
        "Make a grocery list, running low on essentials.",
        "Love the coziness of my living room, perfect for movie nights.",
        "Had a great time at the concert, the music was amazing.",
        "Clean the windows, they're looking a bit dirty.",
        "Love the taste of homemade bread, so much better than store-bought.",
        "Had a peaceful evening at home, watched a good movie.",
        "Enjoyed a quiet evening reading my favorite book, so relaxing.",
        "Organize my kitchen pantry this weekend, it's getting messy.",
    ],
    relevant_noise=[
        "My neighbor at 123 Darwin Avenue threw a huge party last night.",
        "I used to live at 456 Elm Street when I was a kid.",
        "We visited my aunt at 789 Maple Lane during the holidays.",
        "There's a beautiful park near 101 Birch Road that we often visit.",
        "The new bakery on 234 Pine Street has the best pastries.",
        "Our family friend lives at 567 Oak Avenue and has a lovely garden.",
        "I received a package meant for 890 Cedar Drive by mistake.",
        "The house at 345 Willow Lane is up for sale.",
        "I walked past 678 Cherry Street on my way to work.",
        "We had a great barbecue at 901 Ash Boulevard last summer.",
        "My cousin just moved to 123 Birch Drive and loves it there.",
        "There's a nice coffee shop at 456 Maple Street that I frequent.",
        "My best friend grew up at 789 Elm Avenue and has many stories.",
        "We held our annual family reunion at 101 Oak Drive.",
        "There's a new gym opening at 234 Cedar Lane next month.",
        "The house at 567 Pine Boulevard has a fantastic view.",
        "I left my umbrella at 890 Willow Street last week.",
        "The kids love playing at the park on 345 Ash Avenue.",
        "We had our wedding reception at 678 Birch Road.",
        "My grandparents lived at 901 Maple Lane for over 50 years.",
        "My friend Sarah loves pizza, especially from Joe's Pizzeria.",
        "For dinner last night, we had spaghetti with garlic bread.",
        "At the new restaurant, I tried sushi for the first time.",
        "My mom makes the best chocolate cake, hands down.",
        "During our trip, we had fresh seafood by the beach.",
        "My brother's favorite snack is a peanut butter and jelly sandwich.",
        "We enjoyed a delicious brunch with pancakes and bacon.",
        "My dad prefers his steak well-done with a side of mashed potatoes.",
        "We all shared a large bowl of popcorn during the movie night.",
        "I had a refreshing fruit salad for lunch yesterday.",
        "My cousin always orders fried chicken when we eat out.",
        "The pasta primavera at the Italian place was amazing.",
        "We celebrated with a big slice of cheesecake each.",
        "My grandma's homemade soup is perfect on a cold day.",
        "For breakfast, I usually have oatmeal with fresh berries.",
        "We had a wonderful Thanksgiving dinner with all the trimmings.",
        "I tried a new recipe for tacos, and it was a hit.",
        "My niece loves ice cream, especially chocolate flavor.",
        "We had a picnic with sandwiches and lemonade by the lake.",
        "The bakery's croissants were buttery and delicious.",
        "I woke up at 7am this morning to go for a run.",
        "We have a meeting scheduled at 10:30am tomorrow.",
        "Dinner is usually served at our house around 6pm.",
        "The concert starts at 8pm, so we should leave by 7.",
        "Our flight departs at 9:15am, so we need to be at the airport early.",
        "I usually get off work at 5pm and head straight home.",
        "The train to the city leaves at 7:45am sharp.",
        "We had a family gathering at noon to celebrate the holiday.",
        "The fireworks show begins at 9pm every Fourth of July.",
        "The library closes at 8pm, so let's hurry up.",
        "I went for a walk at 6am to enjoy the sunrise.",
        "We have a reservation at the restaurant for 7:30pm.",
        "The store opens at 9am, perfect for early shopping.",
        "Our appointment is at 3pm, don't forget to bring the documents.",
        "The meeting was postponed to 2pm due to unforeseen circumstances.",
        "I usually have lunch around 1pm during weekdays.",
        "The gym class starts at 5:30pm, be there on time.",
        "The movie premiere is at 7pm, let's get good seats.",
        "My alarm goes off at 6:30am every morning.",
        "The football match kicks off at 4pm this Sunday.",
        "I recently visited Paris, France, and it was beautiful.",
        "My best friend, Emily Johnson, is moving to New York City.",
        "We went hiking in the Rocky Mountains last summer.",
        "I met John Smith at a conference last year.",
        "Our family vacationed in San Diego, California, last year.",
        "I work with a colleague named Alice Brown, who is very talented.",
        "We spent a weekend exploring Washington, D.C.",
        "My old neighbor, Michael Davis, just got married.",
        "We traveled to Tokyo, Japan, for a cultural experience.",
        "My cousin, Laura Wilson, is a great cook.",
        "I attended a workshop in Boston, Massachusetts.",
        "My friend, David Lee, is an excellent guitarist.",
        "We visited the Grand Canyon during our road trip.",
        "I have a mentor named Sarah Thomas, who is very inspiring.",
        "Our trip to London, England, was unforgettable.",
        "My neighbor, Robert Martinez, has a beautiful garden.",
        "We took a cruise to the Bahamas last winter.",
        "My colleague, Jessica White, received an award for her work.",
        "We toured the museums in Berlin, Germany, last spring.",
        "I recently met a writer named Charles Moore at a book signing.",
    ],
    embeddable_noise=EmbeddableNoise(
        addresses=[
            "Can you deliver this to <ADDRESS>?",
            "I'd like to order this to <ADDRESS>.",
            "Please send this to <ADDRESS>.",
            "I need this delivered to <ADDRESS>.",
            "The order should go to <ADDRESS>.",
            "Please arrange for this to be delivered to <ADDRESS>.",
            "Can the delivery be made to <ADDRESS>?",
            "I'd like this sent to <ADDRESS>.",
            "The meal needs to go to <ADDRESS>.",
            "Please have this dropped off at <ADDRESS>.",
            "Make sure this arrives at <ADDRESS>.",
            "I want this shipped to <ADDRESS>.",
            "This should be sent to <ADDRESS>.",
            "Deliver this order to <ADDRESS>.",
            "I would like this to be delivered to <ADDRESS>.",
            "Please ensure this is delivered to <ADDRESS>.",
            "Send this to <ADDRESS>, please.",
            "The delivery address is <ADDRESS>.",
            "This order is for <ADDRESS>.",
            "Can you make sure this gets to <ADDRESS>?",
        ],
        foods=EmbeddableNoiseFoods(
            starters=[
                "I'd like to order <STARTERS>.",
                "Can I have <STARTERS> with that?",
                "I'd like to start with <STARTERS>.",
                "Can you add <STARTERS> to my order?",
                "Please include <STARTERS> as an appetizer.",
                "Can you add <STARTERS> to that?",
                "Please add <STARTERS> to my meal.",
            ],
            main=[
                "Please add <MAIN> to my order.",
                "I want <MAIN> as my main dish.",
                "For my main course, I'll have <MAIN>.",
                "I'll have <MAIN> with a side.",
                "I'd like <MAIN> for my entrée.",
                "I'd like to order <MAIN> for dinner.",
                "I'd like <MAIN> as my main course.",
            ],
            desserts=[
                "I'd like <DESSERTS> for dessert.",
                "Please include <DESSERTS> in my order.",
                "I'll take <DESSERTS> for dessert.",
                "I'd like to finish with <DESSERTS>.",
                "For dessert, I'll have <DESSERTS>.",
                "I'll take <DESSERTS> to finish.",
                "For dessert, I'll have <DESSERTS>.",
            ],
            drinks=[
                "I'd like to order <DRINKS> beverage.",
                "Can I have <DRINKS> with that?",
                "Please include <DRINKS> beverage with my meal.",
                "I'd like to add <DRINKS> to my order.",
                "Can you add <DRINKS> beverage to that?",
                "I'll take <DRINKS> with my meal.",
                "Please add <DRINKS> beverage to my order.",
            ],
        ),
        times=[
            "I need this delivered by <TIME>.",
            "Can I schedule the delivery for <TIME>?",
            "I'd like the food to arrive by <TIME>.",
            "Please make sure it gets here by <TIME>.",
            "Can the delivery be made by <TIME>?",
            "I want to place an order for <TIME> delivery.",
            "Please ensure the food is here by <TIME>.",
            "I'd like to set the delivery time to <TIME>.",
            "Can you confirm delivery for <TIME>?",
            "I'd like this to be delivered by <TIME>.",
            "Please make sure my order arrives by <TIME>.",
            "I'd like to have this delivered at <TIME>.",
            "Can the delivery be scheduled for <TIME>?",
            "I'd like my meal to arrive by <TIME>.",
            "Please deliver this by <TIME>.",
            "I'd like to order this for <TIME> delivery.",
            "Make sure it gets here by <TIME>.",
            "Can I have this delivered by <TIME>?",
            "I'd like my food to arrive at <TIME>.",
            "Please ensure delivery by <TIME>.",
        ],
        restaurants=[
            "I'd like to place my order from <RESTAURANT>.",
            "Can I get this meal from <RESTAURANT>?",
            "Please order this from <RESTAURANT>.",
            "I want to order dinner from <RESTAURANT>.",
            "Can you get this dish from <RESTAURANT>?",
            "I'd like to get my food from <RESTAURANT>.",
            "Please place my order at <RESTAURANT>.",
            "I'd like to order lunch from <RESTAURANT>.",
            "Can you arrange delivery from <RESTAURANT>?",
            "I want this meal from <RESTAURANT>.",
            "I'd like to have dinner from <RESTAURANT>.",
            "Please get my order from <RESTAURANT>.",
            "I'd like to get takeout from <RESTAURANT>.",
            "Can you place my order at <RESTAURANT>?",
            "I'd like to have lunch from <RESTAURANT>.",
            "Please order dinner from <RESTAURANT>.",
            "I'd like my meal from <RESTAURANT>.",
            "Can you get lunch from <RESTAURANT>?",
            "I'd like to place a dinner order at <RESTAURANT>.",
            "Please arrange for delivery from <RESTAURANT>.",
        ],
    ),
)