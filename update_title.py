from database import execute_db

execute_db("INSERT OR REPLACE INTO settings (key, value) VALUES ('mandal_name_mr', ?)", ('जागृती चौक गणेशोत्सव मंडळ',))
execute_db("INSERT OR REPLACE INTO settings (key, value) VALUES ('mandal_name_en', ?)", ('Jagriti Chowk Ganeshotsav Mandal',))
print("Database settings table updated successfully!")
