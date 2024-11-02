import psycopg2
import getpass  # For hidden password input
import re       # For input validation
import random

# Function to connect to PostgreSQL database
def connect_db():
    try:
        conn = psycopg2.connect(
            dbname='postgres',
            user='yangjinglan',
            password='123456',
            host='localhost',
            port='5432'
        )
        return conn
    except Exception as e:
        print(f"Error connecting to the database: {e}")
        return None

# Function to hash the password using pgcrypto's crypt
def hash_password(password, cursor):
    cursor.execute("SELECT crypt(%s, gen_salt('bf'))", (password,))
    return cursor.fetchone()[0]

# Function to hash the password using pgcrypto's crypt
def check_password(input_password, stored_hash, cursor):
    cursor.execute("SELECT crypt(%s, %s)", (input_password, stored_hash))
    result = cursor.fetchone()
    return result[0] == stored_hash

def check_instruction_description(recipe_id, cursor):
    cursor.execute("""
        SELECT RecipeId, RecipeName, RecipeDescription, RecipeInstructions
        FROM recipes
        WHERE RecipeId = %s
    """, (recipe_id,))
    recipes = cursor.fetchall()

    if recipes:    
        for recipe in recipes:
            print(f"Recipe ID: {recipe[0]}, Recipe Name: {recipe[1]}")
            print(f"Recipe Description: {recipe[2]}")
            print(f'Recipe Instructions: {recipe[3]}')
    else:
        print("No Description nor Instruction found for this recipe.")

def check_ingredient(recipe_id, cursor):
    cursor.execute("""
        SELECT r.RecipeId, r.RecipeName, i.RecipeIngredientParts, i.RecipeIngredientQuantities
        FROM recipes r
        join ingredients i on r.RecipeId=i.RecipeId
        WHERE r.RecipeId = %s
    """, (recipe_id,))
    recipes = cursor.fetchall()

    if recipes:    
        for recipe in recipes:
            print(f"Recipe ID: {recipe[0]}, Recipe Name: {recipe[1]}")
            print(f"Recipe Ingredient Parts: {recipe[2]}")
            print(f'Recipe Ingredient Quantities: {recipe[3]}')
    else:
        print("No Ingredient found for this recipe.")    

def check_average_rating(recipe_id, cursor):
    cursor.execute("""
        SELECT r.RecipeId, r.RecipeName, avg(rv.Rating)
        FROM reviews rv
        join recipes r on r.RecipeId=rv.RecipeId
        WHERE rv.RecipeId = %s
        group by r.RecipeId
    """, (recipe_id,))
    recipes = cursor.fetchall()

    if recipes:    
        for recipe in recipes:
            print(f"Recipe ID: {recipe[0]}, Recipe Name: {recipe[1]}")
            print(f"Recipe average rating: {recipe[2]}")
    else:
        print("No Rating found for this recipe.")     

def check_all_reviews(recipe_id, cursor):
    cursor.execute("""
        SELECT r.RecipeId, r.RecipeName, rv.ReviewContent
        FROM reviews rv
        join recipes r on r.RecipeId=rv.RecipeId
        WHERE rv.RecipeId = %s
    """, (recipe_id,))
    recipes = cursor.fetchall()

    if recipes:    
        for recipe in recipes:
            print(f"Recipe ID: {recipe[0]}, Recipe Name: {recipe[1]}")
            print(f"Recipe review contens: {recipe[2]}")
    else:
        print("No Review Content found for this recipe.")       


def check_nutrient(recipe_id, cursor):
    cursor.execute("""
        SELECT r.RecipeId, r.RecipeName, n.Calories, n.FatContent, n.SaturatedFatContent, 
                   n.CholesterolContent, n.SodiumContent, n.CarbohydrateContent, n.FiberContent, n.SugarContent, n.ProteinContent
        FROM recipes r
        join nutrients n on r.RecipeId=n.RecipeId
        WHERE r.RecipeId = %s
    """, (recipe_id,))
    recipes = cursor.fetchall()

    if recipes:    
        for recipe in recipes:
            print(f"Recipe ID: {recipe[0]}, Recipe Name: {recipe[1]}")
            print(f"Calories: {recipe[2]}")
            print(f'FatContent: {recipe[3]}')
            print(f'SaturatedFatContent: {recipe[3]}')
            print(f'CholesterolContent: {recipe[3]}')
            print(f'SodiumContent: {recipe[3]}')
            print(f'CarbohydrateContent: {recipe[3]}')
            print(f'FiberContent: {recipe[3]}')
            print(f'SugarContent: {recipe[3]}')
            print(f'ProteinContent: {recipe[3]}')

    else:
        print("No Nutrient found for this recipe.")   

def check_category(recipe_id, cursor):
    cursor.execute("""
        SELECT r.RecipeId, r.RecipeName, c.RecipeCategoryName
        FROM recipes r
        join categories c on r.RecipeId=c.RecipeId
        WHERE r.RecipeId = %s
    """, (recipe_id,))
    recipes = cursor.fetchall()

    if recipes:    
        for recipe in recipes:
            print(f"Recipe ID: {recipe[0]}, Recipe Name: {recipe[1]}")
            print(f'Recipe Category Name: {recipe[2]}')
    else:
        print("No Category found for this recipe.")    



# Function to display author's recipes
def view_author_recipes(user_type,author_id, cursor, conn):
    cursor.execute("""
        SELECT RecipeId, RecipeName FROM recipes
        WHERE AuthorId = %s
    """, (author_id,))
    recipes = cursor.fetchall()
    
    if recipes:
        print(f"Recipes created by Author ID {author_id}:")
        for recipe in recipes:
            print(f"Recipe ID: {recipe[0]}, Recipe Name: {recipe[1]}")
        check_recipe_details(user_type, author_id, cursor, conn)
    else:
        print("No recipes found for this author.")

# Function to handle recipe creation by an author
def create_new_recipe(user_type, author_id, cursor, conn):
    try:
        recipe_name = input("Enter Recipe Name: ")
        recipe_description = input("Enter Recipe Description: ")
        recipe_instructions = input("Enter Recipe Instructions: ")

        ingredient_parts = input("Enter Recipe Ingredient Parts: ")
        ingredient_quantities = input("Enter Recipe Ingredient Quantities: ")

        calories = float(input("Enter Calories(a floating number): "))
        fat_content = float(input("Enter Fat Content(a floating number): "))
        saturated_fat_content = float(input("Enter Saturated Fat Content(a floating number): "))
        cholesterol_content = float(input("Enter Cholesterol Content(a floating number): "))
        sodium_content = float(input("Enter Sodium Content(a floating number): "))
        carbohydrate_content = float(input("Enter Carbohydrate Content(a floating number): "))
        fiber_content = float(input("Enter Fiber Content(a floating number): "))
        sugar_content = float(input("Enter Sugar Content(a floating number): "))
        protein_content = float(input("Enter Protein Content(a floating number): "))

        recipe_category_name = input("Enter Recipe Category Name: ")

        # Automatically generate new IDs
        cursor.execute("SELECT MAX(RecipeId) FROM recipes")
        result = cursor.fetchone()
        new_recipe_id = (result[0] + 1) if result and result[0] else 1

        #cursor.execute("SELECT MAX(TimeId) FROM time")
        #new_time_id = cursor.fetchone()[0] + 1 if cursor.fetchone()[0] else 1

        cursor.execute("SELECT MAX(IngredientId) FROM ingredients")
        result = cursor.fetchone()
        new_ingredient_id = (result[0] + 1) if result and result[0] else 1

        cursor.execute("SELECT MAX(NutrientId) FROM nutrients")
        result = cursor.fetchone()
        new_nutrient_id = (result[0] + 1) if result and result[0] else 1

        cursor.execute("SELECT MAX(RecipeCategoryId) FROM categories")
        result = cursor.fetchone()
        new_category_id = (result[0] + 1) if result and result[0] else 1

        # Insert data into `recipes`
        cursor.execute("""
            INSERT INTO recipes (RecipeId, RecipeName, RecipeDescription, RecipeInstructions, AuthorId)
            VALUES (%s, %s, %s, %s, %s)
        """, (new_recipe_id, recipe_name, recipe_description, recipe_instructions, author_id))

        # Insert data into `time`
        #cursor.execute("""
            #INSERT INTO time (TimeId, RecipeId, CookTime, PrepTime, TotalTime)
            #VALUES (%s, %s, %s, %s, %s)
        #""", (new_time_id, new_recipe_id, cook_time, prep_time, total_time))

        # Insert data into `ingredients`
        cursor.execute("""
            INSERT INTO ingredients (IngredientId, RecipeId, RecipeIngredientParts, RecipeIngredientQuantities)
            VALUES (%s, %s, %s, %s)
        """, (new_ingredient_id, new_recipe_id, ingredient_parts, ingredient_quantities))

        # Insert data into `nutrients`
        cursor.execute("""
            INSERT INTO nutrients (NutrientId, RecipeId, Calories, FatContent, SaturatedFatContent, CholesterolContent, 
                                SodiumContent, CarbohydrateContent, FiberContent, SugarContent, ProteinContent)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """, (new_nutrient_id, new_recipe_id, calories, fat_content, saturated_fat_content, cholesterol_content,
            sodium_content, carbohydrate_content, fiber_content, sugar_content, protein_content))

        # Insert data into `categories`
        cursor.execute("""
            INSERT INTO categories (RecipeCategoryId, RecipeCategoryName, RecipeId)
            VALUES (%s, %s, %s)
        """, (new_category_id, recipe_category_name, new_recipe_id))

        conn.commit()
        print(f"Recipe '{recipe_name}' successfully added!")
        print("Direct to Last Step")
        author_post_login(user_type, author_id, cursor, conn)
    except:
        print(f"Recipe creation fails! Please try again")
        create_new_recipe(user_type, author_id, cursor, conn)


# Function to handle post-login options for author
def author_post_login(user_type, author_id, cursor, conn):
    print("1. View your uploaded recipes")
    print("2. Upload a new recipe")
    choice = input("Choose an option (1 or 2): ")

    if choice == '1':
        view_author_recipes(user_type,author_id, cursor, conn)
    elif choice == '2':
        create_new_recipe(user_type, author_id, cursor, conn)
    else:
        print("Invalid choice. Please choose 1 or 2.")
        author_post_login(author_id, cursor, conn)

def check_recipe_details(user_type, user_id, cursor, conn):
        print("1. View description and instruction for a specific recipe")
        print("2. View ingredient for a specific recipe")
        print("3. View nutrients for a specific recipe")
        print("4. View category for a specific recipe")
        print("5. View average rating for a specific recipe")
        print("6. View all reviews for a specific recipe")
        print("7. Return to Last step")
        choice = input("Choose an option (1, 2, 3, 4, 5, 6, or 7): ")

        if choice == '7':
            if user_type == 'author':
                author_post_login(user_type, user_id, cursor, conn)
            else:
                reviewer_post_login(user_type, user_id, cursor, conn)
        recipe_id = input(f"Enter recipe ID: ")
        if choice == '1':
            check_instruction_description(recipe_id, cursor)
        elif choice == '2':
            check_ingredient(recipe_id, cursor)
        elif choice == '3':
            check_nutrient(recipe_id, cursor)
        elif choice == '4':
            check_category(recipe_id, cursor)
        elif choice == '5':
            check_average_rating(recipe_id, cursor)
        elif choice == '6':
            check_all_reviews(recipe_id, cursor)      

        else:
            print("Invalid choice. Please choose 1, 2, 3, 4, 5, or 6.")
            check_recipe_details(cursor)

# Function to view recipes previously reviewed by the reviewer
def view_reviewed_recipes_by_reviewer(user_type, reviewer_id, cursor, conn):
    cursor.execute("""
        SELECT r.RecipeId, r.RecipeName, rv.ReviewContent, rv.Rating
        FROM recipes r
        JOIN reviews rv ON r.RecipeId = rv.RecipeId
        WHERE rv.ReviewerId = %s
    """, (reviewer_id,))
    reviews = cursor.fetchall()
    if reviews:
        print("Recipes you have reviewed:")
        for review in reviews:
            print(f"RecipeId: {review[0]}, RecipeName: {review[1]}")
            print(f"ReviewContent: {review[2]}, Rating: {review[3]}")
        check_recipe_details(user_type,reviewer_id, cursor, conn)
    else:
        print("You haven't reviewed any recipes yet.")


def create_new_review(reviewer_id, cursor, conn):
    recipe_id = input("Enter Recipe id: ")
    #recipe_name = input("Enter Recipe Name: ")
    Review_Content = input("Enter Review Content: ")
    Rating = float(input("Enter Rating(a float number): "))

    cursor.execute("SELECT MAX(ReviewId) FROM reviews")
    result = cursor.fetchone()
    new_review_id = (result[0] + 1) if result and result[0] else 1

    # Insert data into `reviews`
    cursor.execute("""
        INSERT INTO reviews (ReviewId, ReviewerId, RecipeId, ReviewContent, Rating)
        VALUES (%s, %s, %s, %s, %s)
    """, (new_review_id, reviewer_id, recipe_id, Review_Content, Rating))   

    conn.commit()
    print(f"Recipe id '{recipe_id}' successfully reviewed!")



def post_category(reviewer_id,cursor, conn):
    print("1. View details of a recipe")
    print("2. Write a review for a recipe")

    choice = input("Choose an option (1 or 2): ")

    if choice == '1':
        check_recipe_details('reviewer', reviewer_id, cursor, conn)
    elif choice == '2':
        create_new_review(reviewer_id, cursor, conn)
    else:
        print("Invalid choice. Please choose 1 or 2.")
        post_category(cursor)

# Function to view recipes by category
def view_recipes_by_category(reviewer_id,cursor, conn):
    category_name = input("Enter a Recipe Category Name: ")
    
    # Use ILIKE for case-insensitive partial matching
    cursor.execute("""
        SELECT RecipeCategoryId 
        FROM categories 
        WHERE RecipeCategoryName ILIKE %s
    """, ('%' + category_name + '%',))  # '%' allows partial matching
    result = cursor.fetchall()  # Fetch all matching categories
    
    if result:
        # Loop through all matching categories to fetch their recipes
        for category in result:
            category_id = category[0]
            # Fetch 10 random recipes in the matching categories
            cursor.execute("""
                SELECT r.RecipeId, r.RecipeName
                FROM recipes r
                JOIN categories c ON r.RecipeId = c.RecipeId
                WHERE c.RecipeCategoryId = %s
            """, (category_id,))
            recipes = cursor.fetchall()

            if recipes:
                # Randomly select up to 10 recipes from the list
                selected_recipes = random.sample(recipes, min(10, len(recipes)))
                print(f"Recipes in the category matching '{category_name}':")
                for recipe in selected_recipes:
                    print(f"RecipeId: {recipe[0]}, RecipeName: {recipe[1]}")
                post_category(reviewer_id,cursor, conn)

            else:
                print(f"No recipes found for category ID: {category_id}")
                view_recipes_by_category(cursor)
    else:
        print(f"No categories found matching '{category_name}'.")
        view_recipes_by_category(cursor)

# Function to handle post-login options for author
def reviewer_post_login(user_type, reviewer_id, cursor, conn):
    print("What would you like to do?")
    print("1. View recipes I have reviewed")
    print("2. View new recipes by category")
    print("3. Write review for a recipe")
    print("4. Exit")
    action = input("Enter 1, 2, 3, or 4: ")

    if action == "1":
        view_reviewed_recipes_by_reviewer(user_type, reviewer_id, cursor, conn)
    elif action == "2":
        view_recipes_by_category(reviewer_id, cursor,conn)
    elif action == "3":
        create_new_review(reviewer_id, cursor, conn)
    elif action == "4":
        print("Exit successfully.")
        return
    else:
        print("Invalid option. Please try again.")

# Function to handle user login
def user_login(user_type, cursor, conn):
    if user_type == 'author':
        table = 'authors'
        id_column = 'AuthorId'
        name_column = 'AuthorName'
        password_column = 'AuthorPassword'
    else:
        table = 'reviewers'
        id_column = 'ReviewerId'
        name_column = 'ReviewerName'
        password_column = 'ReviewerPassword'

    user_id = input(f"Enter {user_type} ID: ")
    user_password = getpass.getpass(f"Enter {user_type} password: ")

    # Fetch the stored password hash for the given user ID
    
    cursor.execute(f"SELECT crypt({password_column},gen_salt('bf'))  FROM {table} WHERE {id_column} = %s", (user_id,))
    result = cursor.fetchone()

    if result:
        stored_password = result[0]
        # Verify the password using the stored hash
        if check_password(user_password, stored_password, cursor):
            cursor.execute(f"SELECT {name_column}  FROM {table} WHERE {id_column} = %s", (user_id,))
            name = cursor.fetchone()[0]
            print(f"Welcome! {name}")
            print(f"Login successful as {user_type}!")
            if user_type == 'author':
                author_post_login(user_type,user_id, cursor, conn)  # Handle author-specific options
            else:
                reviewer_post_login(user_type,user_id, cursor, conn)
        else:
            print("Incorrect password. Please try again.")
            user_login(user_type, cursor, conn)  # Retry login if password is wrong
    else:
        print(f"No {user_type} found with ID {user_id}. Please try again.")
        user_login(user_type, cursor, conn)

# Function to check if the user ID already exists
def is_id_unique(user_id, table, id_column, cursor):
    cursor.execute(f"SELECT 1 FROM {table} WHERE {id_column} = %s", (user_id,))
    return cursor.fetchone() is None

# Function to handle user registration
def user_register(user_type, cursor, conn):
    if user_type == 'author':
        table = 'authors'
        id_column = 'AuthorId'
        name_column = 'AuthorName'
        password_column = 'AuthorPassword'
    else:
        table = 'reviewers'
        id_column = 'ReviewerId'
        name_column = 'ReviewerName'
        password_column = 'ReviewerPassword'

    # Get valid 10-digit user ID and check uniqueness
    while True:
        user_id = input(f"Enter a 10-digit {user_type} ID: ")
        if re.fullmatch(r'\d{10}', user_id):
            if is_id_unique(user_id, table, id_column, cursor):
                break
            else:
                print(f"The {user_type} ID already exists. Please choose a different ID.")
        else:
            print("Invalid ID. Please enter exactly 10 digits.")

    # Get valid 6-digit password
    while True:
        user_password = getpass.getpass(f"Enter a 6-digit {user_type} password: ")
        if re.fullmatch(r'\d{6}', user_password):
            break
        else:
            print("Invalid password. Please enter exactly 6 digits.")

    # Get the username
    user_name = input(f"Enter {user_type} name: ")

    # Hash the password and insert the new user into the table
    #hashed_password = hash_password(user_password, cursor)
    try:
        cursor.execute(f"INSERT INTO {table} ({id_column}, {name_column}, {password_column}) VALUES (%s, %s, %s)",
                       (user_id, user_name, user_password))
        conn.commit()
        print(f"{user_type.capitalize()} registered successfully!")
        print("Direct back to Login Page.")
        main()
    except Exception as e:
        print(f"Error registering {user_type}: {e}")
        conn.rollback()

# Main function for CLI interaction
def main():
    conn = connect_db()
    if conn is None:
        return
    cursor = conn.cursor()

    # Ask user to choose login or registration
    print("Welcome to the Food Recipe Website!")
    print("1. Login")
    print("2. Register")
    #print("3. Close an account")
    print("3. Exit")
    choice = input("Please choose your action (1, 2, or 3): ")

    if choice == '1':
        # Ask user to choose login type
        print("1. Author login")
        print("2. Reviewer login")
        print("3. Go back to Last step")
        user_type = input("Please choose your role (1, 2, or 3): ")
        if user_type == '1':
            user_login('author', cursor, conn)
        elif user_type == '2':
            user_login('reviewer', cursor, conn)
        elif user_type == '3':
            main()
        else:
            print("Invalid choice. Please choose 1, 2, or 3.")
            main()  # Retry if invalid input
    elif choice == '2':
        # Ask user to choose registration type
        print("1. Author registration")
        print("2. Reviewer registration")
        print("3. Go back to Last step")
        user_type = input("Please choose your role (1, 2, or 3): ")
        if user_type == '1':
            user_register('author', cursor, conn)
        elif user_type == '2':
            user_register('reviewer', cursor, conn)
        elif user_type == '3':
            main()            
        else:
            print("Invalid choice. Please choose 1, 2, or 3.")
            main()  # Retry if invalid input      
    elif choice == '3':
        print("Exit successfully.")
    else:
        print("Invalid choice. Please choose 1, 2, or 2.")
        main()  # Retry if invalid input

    cursor.close()
    conn.close()

if __name__ == '__main__':
    main()