purchase_total = "SUM(p.total) AS total"
purchase_count = "COUNT(p.id) AS purchase_count"
purchase_date = "p.purchase_date AS date"
purchase_day = "strftime ('%d', p.purchase_date) AS day"
purchase_month = "strftime ('%m', p.purchase_date) AS month"
purchase_year = "strftime ('%Y', p.purchase_date) AS year"


# Total
total_all_time_query = """SELECT SUM(total) FROM purchase;"""

total_per_month_query = """SELECT 
	strftime ('%m', p.purchase_date) AS month,
	SUM(p.total) AS total
FROM purchase p
GROUP BY month;"""

total_per_month_with_purchase_count = """SELECT 
	strftime('%m', p.purchase_date) AS month,
	SUM(p.total) AS total,
	COUNT(p.id) as purchase_count
FROM purchase p
GROUP BY month;"""

total_per_given_months = """SELECT 
	strftime('%m', p.purchase_date) AS month,
	SUM(p.total) AS total
FROM purchase p 
WHERE month IN (%s)
GROUP BY month;"""

total_per_given_months_purchase_count = """SELECT 
	strftime('%m', p.purchase_date) AS month,
	SUM(p.total) AS total,
	COUNT(p.id) as purchase_count
FROM purchase p
WHERE month IN (%s)
GROUP BY month;"""

total_per_given_stores = """SELECT
	s.name AS store_name,
	SUM(p.total) AS total
FROM store s
INNER JOIN purchase p ON s.id = p.store_id
WHERE s.name IN (%s)
GROUP BY store_name;"""

total_per_given_stores_with_purchase_count = """SELECT
	s.name AS store_name,
	SUM(p.total) AS total,
	COUNT(p.id) as purchase_count
FROM store s
INNER JOIN purchase p ON s.id = p.store_id
WHERE s.name IN (%s)
GROUP BY store_name;"""

total_per_store = """SELECT 
	s.name as store_name, 
	SUM(p.total) as total
FROM store s 
INNER JOIN purchase p ON s.id = p.store_id
GROUP BY store_name;"""

total_per_store_with_purchase_count = """SELECT 
	s.name as store_name, 
	SUM(p.total) as total,
	COUNT(p.id) as purchase_count
FROM store s 
INNER JOIN purchase p ON s.id = p.store_id
GROUP BY store_name;"""
