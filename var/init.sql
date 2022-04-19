CREATE TABLE IF NOT EXISTS public.url_visited (url TEXT, visited BOOLEAN);
CREATE TABLE IF NOT EXISTS public.recipes
 (title TEXT, html TEXT , ingredients, rating , reviews, instructions, author, url, url_id, tags, amount_comments)