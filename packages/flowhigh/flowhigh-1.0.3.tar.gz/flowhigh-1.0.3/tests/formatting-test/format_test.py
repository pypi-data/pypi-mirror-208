import unittest
from flowhigh.format.formatting import _process_data


class FormatterTest(unittest.TestCase):

    @classmethod
    def setup(cls, marked_sql: str, option: str = "compact") -> str:
        return _process_data(marked_sql, option)

    def test_second_new_line(self):
        marked_sql = """SELECT p1 ✖,p2 ✖"""

        expected = """SELECT p1 
,p2 """
        self.assertEqual(expected, self.setup(marked_sql))

    def test_anchor(self):
        marked_sql = """SELECT⚓ p1 ✖⚓,p2 ✖⚓"""

        expected = """SELECT p1 
      ,p2 
      """

        self.assertEqual(expected, self.setup(marked_sql))

    def test_nested_anchor(self):
        marked_sql = """❌FROM⚓(➕SELECT⚓ op1.OrderID ✖⚓,op1.ProductID as ⛓⚓p1"""

        expected = """  FROM(SELECT op1.OrderID 
             ,op1.ProductID as p1"""

        self.assertEqual(expected, self.setup(marked_sql))

    def test_optional_new_line(self):
        marked_sql = """❌FROM⚓(➕SELECT⚓ op1.OrderID ✖⚓,op1.ProductID as ⛓⚓p1"""

        expected = """  FROM(SELECT op1.OrderID 
             ,op1.ProductID as 
             p1"""

        self.assertEqual(expected, self.setup(marked_sql, "comfortable"))

    def test_compact_marker(self):
        marked_sql = """op1.OrderID⚫=⚫op2.OrderID"""

        expected = """op1.OrderID=op2.OrderID"""

        self.assertEqual(expected, self.setup(marked_sql))

    def test_first_new_line(self):
        marked_sql = """SELECT ❌FROM"""

        expected = """SELECT 
FROM"""

        self.assertEqual(expected, self.setup(marked_sql))

    def test_first_new_line(self):
        marked_sql = """SELECT ❌FROM"""

        expected = """SELECT 
FROM"""

        self.assertEqual(expected, self.setup(marked_sql))

    def test_sample_regular_compact(self):
        marked_sql = """WITH← all_sales AS(➕❌SELECT⚓ d.year ✖⚓,i.brand_id ✖⚓,i.class_id ✖⚓,i.category_id ✖⚓,i.manufact_id ✖⚓,SUM(➕sales_cnt➖) AS ⛓⚓sales_cnt ✖⚓,SUM(➕sales_amt➖) AS ⛓⚓sales_amt❌FROM⚓(➕SELECT⚓ d.year ✖⚓,i.brand_id ✖⚓,i.class_id ✖⚓,i.category_id ✖⚓,i.manufact_id ✖⚓,cs.quantity ⚫-⚫ COALESCE(➕cr.return_quantity✖⚓,0➖) AS ⛓⚓sales_cnt ✖⚓,cs.ext_sales_price ⚫-⚫ COALESCE(➕cr.return_amount✖⚓,0.0➖) AS ⛓⚓sales_amt ❌FROM⚓ catalog_sales cs ❌JOIN⚓ item i ❌ON⚓ i.item_sk ⚫=⚫ cs.item_sk ❌JOIN⚓ date_dim d ❌ON⚓ d.date_sk ⚫=⚫ cs.sold_date_sk ❌LEFT⚓ ❌JOIN⚓ catalog_returns cr ❌ON⚓(➕cs.order_number ⚫=⚫ cr.order_number ✖AND⚓ cs.item_sk ⚫=⚫ cr.item_sk➖) ❌WHERE⚓ i.category ⚫=⚫ 'Shoes' ❌UNION⚓❌ SELECT⚓ d.year ✖⚓,i.brand_id ✖⚓,i.class_id ✖⚓,i.category_id ✖⚓,i.manufact_id ✖⚓,ss.quantity ⚫-⚫ COALESCE(➕sr.return_quantity✖⚓,0➖) AS ⛓⚓sales_cnt ✖⚓,ss.ext_sales_price ⚫-⚫ COALESCE(➕sr.return_amt✖⚓,0.0➖) AS ⛓⚓sales_amt ❌FROM⚓ store_sales ss ❌JOIN⚓ item i ❌ON⚓ i.item_sk ⚫=⚫ ss.item_sk ❌JOIN⚓ date_dim d ❌ON⚓ d.date_sk ⚫=⚫ ss.sold_date_sk ❌LEFT⚓ ❌JOIN⚓ store_returns sr ❌ON⚓(➕ss.ticket_number ⚫=⚫ sr.ticket_number ✖AND⚓ ss.item_sk ⚫=⚫ sr.item_sk➖) ❌WHERE⚓ i.category ⚫=⚫ 'Shoes' ❌UNION⚓❌ SELECT⚓ d.year ✖⚓,i.brand_id ✖⚓,i.class_id ✖⚓,i.category_id ✖⚓,i.manufact_id ✖⚓,ws.quantity ⚫-⚫ COALESCE(➕wr.return_quantity✖⚓,0➖) AS ⛓⚓sales_cnt ✖⚓,ws.ext_sales_price ⚫-⚫ COALESCE(➕wr.return_amt✖⚓,0.0➖) AS ⛓⚓sales_amt ❌FROM⚓ web_sales ws ❌JOIN⚓ item i ❌ON⚓ i.item_sk ⚫=⚫ ws.item_sk ❌JOIN⚓ date_dim d ❌ON⚓ d.date_sk ⚫=⚫ ws.sold_date_sk ❌LEFT⚓ ❌JOIN⚓ web_returns wr ❌ON⚓(➕ws.order_number ⚫=⚫ wr.order_number ✖AND⚓ ws.item_sk ⚫=⚫ wr.item_sk➖) ❌WHERE⚓ i.category ⚫=⚫ 'Shoes'➖) sales_detail ❌GROUP⚓ BY d.year✖⚓,i.brand_id✖⚓,i.class_id✖⚓,i.category_id✖⚓,i.manufact_id⛓⚓➖)❌SELECT⚓ prev_yr.d_year AS ⛓⚓prev_year ✖⚓,curr_yr.d_year AS ⛓⚓year ✖⚓,curr_yr.i_brand_id ✖⚓,curr_yr.i_class_id ✖⚓,curr_yr.i_category_id ✖⚓,curr_yr.i_manufact_id ✖⚓,prev_yr.sales_cnt AS ⛓⚓prev_yr_cnt ✖⚓,curr_yr.sales_cnt AS ⛓⚓curr_yr_cnt ✖⚓,curr_yr.sales_cnt ⚫-⚫ prev_yr.sales_cnt AS ⛓⚓sales_cnt_diff ✖⚓,curr_yr.sales_amt ⚫-⚫ prev_yr.sales_amt AS ⛓⚓sales_amt_diff❌FROM⚓ all_sales curr_yr✖⚓,all_sales prev_yr❌WHERE⚓ curr_yr.brand_id ⚫=⚫ prev_yr.brand_id ✖AND⚓ curr_yr.class_id ⚫=⚫ prev_yr.class_id ✖AND⚓ curr_yr.category_id ⚫=⚫ prev_yr.category_id ✖AND⚓ curr_yr.manufact_id ⚫=⚫ prev_yr.manufact_id ✖AND⚓ curr_yr.year ⚫=⚫ 2000 ✖AND⚓ prev_yr.year ⚫=⚫ 2000 ⚫-⚫ 1 ✖AND⚓ CAST(➕curr_yr.sales_cnt AS DECIMAL(➕17✖⚓,2➖)➖) ⚫/⚫ CAST(➕prev_yr.sales_cnt AS DECIMAL(➕17✖⚓,2➖)➖) ⚫<⚫ 0.9❌ORDER⚓ BY sales_cnt_diff❌limit⚓ 100"""

        compact = """WITH all_sales AS(
    SELECT d.year 
          ,i.brand_id 
          ,i.class_id 
          ,i.category_id 
          ,i.manufact_id 
          ,SUM(sales_cnt) AS sales_cnt 
          ,SUM(sales_amt) AS sales_amt
      FROM(SELECT d.year 
                 ,i.brand_id 
                 ,i.class_id 
                 ,i.category_id 
                 ,i.manufact_id 
                 ,cs.quantity-COALESCE(cr.return_quantity
                  ,0) AS sales_cnt 
                 ,cs.ext_sales_price-COALESCE(cr.return_amount
                  ,0.0) AS sales_amt 
             FROM catalog_sales cs 
             JOIN item i 
               ON i.item_sk=cs.item_sk
             JOIN date_dim d 
               ON d.date_sk=cs.sold_date_sk
             LEFT 
             JOIN catalog_returns cr 
               ON(cs.order_number=cr.order_number
               AND cs.item_sk=cr.item_sk)
            WHERE i.category='Shoes'
            UNION
           SELECT d.year 
                 ,i.brand_id 
                 ,i.class_id 
                 ,i.category_id 
                 ,i.manufact_id 
                 ,ss.quantity-COALESCE(sr.return_quantity
                  ,0) AS sales_cnt 
                 ,ss.ext_sales_price-COALESCE(sr.return_amt
                  ,0.0) AS sales_amt 
             FROM store_sales ss 
             JOIN item i 
               ON i.item_sk=ss.item_sk
             JOIN date_dim d 
               ON d.date_sk=ss.sold_date_sk
             LEFT 
             JOIN store_returns sr 
               ON(ss.ticket_number=sr.ticket_number
               AND ss.item_sk=sr.item_sk)
            WHERE i.category='Shoes'
            UNION
           SELECT d.year 
                 ,i.brand_id 
                 ,i.class_id 
                 ,i.category_id 
                 ,i.manufact_id 
                 ,ws.quantity-COALESCE(wr.return_quantity
                  ,0) AS sales_cnt 
                 ,ws.ext_sales_price-COALESCE(wr.return_amt
                  ,0.0) AS sales_amt 
             FROM web_sales ws 
             JOIN item i 
               ON i.item_sk=ws.item_sk
             JOIN date_dim d 
               ON d.date_sk=ws.sold_date_sk
             LEFT 
             JOIN web_returns wr 
               ON(ws.order_number=wr.order_number
               AND ws.item_sk=wr.item_sk)
            WHERE i.category='Shoes') sales_detail
     GROUP BY d.year
          ,i.brand_id
          ,i.class_id
          ,i.category_id
          ,i.manufact_id)
SELECT prev_yr.d_year AS prev_year 
      ,curr_yr.d_year AS year 
      ,curr_yr.i_brand_id 
      ,curr_yr.i_class_id 
      ,curr_yr.i_category_id 
      ,curr_yr.i_manufact_id 
      ,prev_yr.sales_cnt AS prev_yr_cnt 
      ,curr_yr.sales_cnt AS curr_yr_cnt 
      ,curr_yr.sales_cnt-prev_yr.sales_cnt AS sales_cnt_diff
      ,curr_yr.sales_amt-prev_yr.sales_amt AS sales_amt_diff
  FROM all_sales curr_yr
      ,all_sales prev_yr
 WHERE curr_yr.brand_id=prev_yr.brand_id
   AND curr_yr.class_id=prev_yr.class_id
   AND curr_yr.category_id=prev_yr.category_id
   AND curr_yr.manufact_id=prev_yr.manufact_id
   AND curr_yr.year=2000
   AND prev_yr.year=2000-1
   AND CAST(curr_yr.sales_cnt AS DECIMAL(17
                 ,2))/CAST(prev_yr.sales_cnt AS DECIMAL(17
                 ,2))<0.9
 ORDER BY sales_cnt_diff
 limit 100"""

        self.assertEqual(compact, _process_data(marked_sql, "compact"))

    def test_sample_regular_balanced(self):
        marked_sql = """WITH← all_sales AS(➕❌SELECT⚓ d.year ✖⚓,i.brand_id ✖⚓,i.class_id ✖⚓,i.category_id ✖⚓,i.manufact_id ✖⚓,SUM(➕sales_cnt➖) AS ⛓⚓sales_cnt ✖⚓,SUM(➕sales_amt➖) AS ⛓⚓sales_amt❌FROM⚓(➕SELECT⚓ d.year ✖⚓,i.brand_id ✖⚓,i.class_id ✖⚓,i.category_id ✖⚓,i.manufact_id ✖⚓,cs.quantity ⚫-⚫ COALESCE(➕cr.return_quantity✖⚓,0➖) AS ⛓⚓sales_cnt ✖⚓,cs.ext_sales_price ⚫-⚫ COALESCE(➕cr.return_amount✖⚓,0.0➖) AS ⛓⚓sales_amt ❌FROM⚓ catalog_sales cs ❌JOIN⚓ item i ❌ON⚓ i.item_sk ⚫=⚫ cs.item_sk ❌JOIN⚓ date_dim d ❌ON⚓ d.date_sk ⚫=⚫ cs.sold_date_sk ❌LEFT⚓ ❌JOIN⚓ catalog_returns cr ❌ON⚓(➕cs.order_number ⚫=⚫ cr.order_number ✖AND⚓ cs.item_sk ⚫=⚫ cr.item_sk➖) ❌WHERE⚓ i.category ⚫=⚫ 'Shoes' ❌UNION⚓❌ SELECT⚓ d.year ✖⚓,i.brand_id ✖⚓,i.class_id ✖⚓,i.category_id ✖⚓,i.manufact_id ✖⚓,ss.quantity ⚫-⚫ COALESCE(➕sr.return_quantity✖⚓,0➖) AS ⛓⚓sales_cnt ✖⚓,ss.ext_sales_price ⚫-⚫ COALESCE(➕sr.return_amt✖⚓,0.0➖) AS ⛓⚓sales_amt ❌FROM⚓ store_sales ss ❌JOIN⚓ item i ❌ON⚓ i.item_sk ⚫=⚫ ss.item_sk ❌JOIN⚓ date_dim d ❌ON⚓ d.date_sk ⚫=⚫ ss.sold_date_sk ❌LEFT⚓ ❌JOIN⚓ store_returns sr ❌ON⚓(➕ss.ticket_number ⚫=⚫ sr.ticket_number ✖AND⚓ ss.item_sk ⚫=⚫ sr.item_sk➖) ❌WHERE⚓ i.category ⚫=⚫ 'Shoes' ❌UNION⚓❌ SELECT⚓ d.year ✖⚓,i.brand_id ✖⚓,i.class_id ✖⚓,i.category_id ✖⚓,i.manufact_id ✖⚓,ws.quantity ⚫-⚫ COALESCE(➕wr.return_quantity✖⚓,0➖) AS ⛓⚓sales_cnt ✖⚓,ws.ext_sales_price ⚫-⚫ COALESCE(➕wr.return_amt✖⚓,0.0➖) AS ⛓⚓sales_amt ❌FROM⚓ web_sales ws ❌JOIN⚓ item i ❌ON⚓ i.item_sk ⚫=⚫ ws.item_sk ❌JOIN⚓ date_dim d ❌ON⚓ d.date_sk ⚫=⚫ ws.sold_date_sk ❌LEFT⚓ ❌JOIN⚓ web_returns wr ❌ON⚓(➕ws.order_number ⚫=⚫ wr.order_number ✖AND⚓ ws.item_sk ⚫=⚫ wr.item_sk➖) ❌WHERE⚓ i.category ⚫=⚫ 'Shoes'➖) sales_detail ❌GROUP⚓ BY d.year✖⚓,i.brand_id✖⚓,i.class_id✖⚓,i.category_id✖⚓,i.manufact_id⛓⚓➖)❌SELECT⚓ prev_yr.d_year AS ⛓⚓prev_year ✖⚓,curr_yr.d_year AS ⛓⚓year ✖⚓,curr_yr.i_brand_id ✖⚓,curr_yr.i_class_id ✖⚓,curr_yr.i_category_id ✖⚓,curr_yr.i_manufact_id ✖⚓,prev_yr.sales_cnt AS ⛓⚓prev_yr_cnt ✖⚓,curr_yr.sales_cnt AS ⛓⚓curr_yr_cnt ✖⚓,curr_yr.sales_cnt ⚫-⚫ prev_yr.sales_cnt AS ⛓⚓sales_cnt_diff ✖⚓,curr_yr.sales_amt ⚫-⚫ prev_yr.sales_amt AS ⛓⚓sales_amt_diff❌FROM⚓ all_sales curr_yr✖⚓,all_sales prev_yr❌WHERE⚓ curr_yr.brand_id ⚫=⚫ prev_yr.brand_id ✖AND⚓ curr_yr.class_id ⚫=⚫ prev_yr.class_id ✖AND⚓ curr_yr.category_id ⚫=⚫ prev_yr.category_id ✖AND⚓ curr_yr.manufact_id ⚫=⚫ prev_yr.manufact_id ✖AND⚓ curr_yr.year ⚫=⚫ 2000 ✖AND⚓ prev_yr.year ⚫=⚫ 2000 ⚫-⚫ 1 ✖AND⚓ CAST(➕curr_yr.sales_cnt AS DECIMAL(➕17✖⚓,2➖)➖) ⚫/⚫ CAST(➕prev_yr.sales_cnt AS DECIMAL(➕17✖⚓,2➖)➖) ⚫<⚫ 0.9❌ORDER⚓ BY sales_cnt_diff❌limit⚓ 100"""

        expected = """WITH all_sales AS(
    SELECT d.year 
          ,i.brand_id 
          ,i.class_id 
          ,i.category_id 
          ,i.manufact_id 
          ,SUM(sales_cnt) AS sales_cnt 
          ,SUM(sales_amt) AS sales_amt
      FROM(SELECT d.year 
                 ,i.brand_id 
                 ,i.class_id 
                 ,i.category_id 
                 ,i.manufact_id 
                 ,cs.quantity - COALESCE(cr.return_quantity
                  ,0) AS sales_cnt 
                 ,cs.ext_sales_price - COALESCE(cr.return_amount
                  ,0.0) AS sales_amt 
             FROM catalog_sales cs 
             JOIN item i 
               ON i.item_sk = cs.item_sk
             JOIN date_dim d 
               ON d.date_sk = cs.sold_date_sk
             LEFT 
             JOIN catalog_returns cr 
               ON(cs.order_number = cr.order_number
               AND cs.item_sk = cr.item_sk)
            WHERE i.category = 'Shoes'
            UNION
           SELECT d.year 
                 ,i.brand_id 
                 ,i.class_id 
                 ,i.category_id 
                 ,i.manufact_id 
                 ,ss.quantity - COALESCE(sr.return_quantity
                  ,0) AS sales_cnt 
                 ,ss.ext_sales_price - COALESCE(sr.return_amt
                  ,0.0) AS sales_amt 
             FROM store_sales ss 
             JOIN item i 
               ON i.item_sk = ss.item_sk
             JOIN date_dim d 
               ON d.date_sk = ss.sold_date_sk
             LEFT 
             JOIN store_returns sr 
               ON(ss.ticket_number = sr.ticket_number
               AND ss.item_sk = sr.item_sk)
            WHERE i.category = 'Shoes'
            UNION
           SELECT d.year 
                 ,i.brand_id 
                 ,i.class_id 
                 ,i.category_id 
                 ,i.manufact_id 
                 ,ws.quantity - COALESCE(wr.return_quantity
                  ,0) AS sales_cnt 
                 ,ws.ext_sales_price - COALESCE(wr.return_amt
                  ,0.0) AS sales_amt 
             FROM web_sales ws 
             JOIN item i 
               ON i.item_sk = ws.item_sk
             JOIN date_dim d 
               ON d.date_sk = ws.sold_date_sk
             LEFT 
             JOIN web_returns wr 
               ON(ws.order_number = wr.order_number
               AND ws.item_sk = wr.item_sk)
            WHERE i.category = 'Shoes') sales_detail
     GROUP BY d.year
          ,i.brand_id
          ,i.class_id
          ,i.category_id
          ,i.manufact_id)
SELECT prev_yr.d_year AS prev_year 
      ,curr_yr.d_year AS year 
      ,curr_yr.i_brand_id 
      ,curr_yr.i_class_id 
      ,curr_yr.i_category_id 
      ,curr_yr.i_manufact_id 
      ,prev_yr.sales_cnt AS prev_yr_cnt 
      ,curr_yr.sales_cnt AS curr_yr_cnt 
      ,curr_yr.sales_cnt - prev_yr.sales_cnt AS sales_cnt_diff
      ,curr_yr.sales_amt - prev_yr.sales_amt AS sales_amt_diff
  FROM all_sales curr_yr
      ,all_sales prev_yr
 WHERE curr_yr.brand_id = prev_yr.brand_id
   AND curr_yr.class_id = prev_yr.class_id
   AND curr_yr.category_id = prev_yr.category_id
   AND curr_yr.manufact_id = prev_yr.manufact_id
   AND curr_yr.year = 2000
   AND prev_yr.year = 2000 - 1
   AND CAST(curr_yr.sales_cnt AS DECIMAL(17
                 ,2)) / CAST(prev_yr.sales_cnt AS DECIMAL(17
                 ,2)) < 0.9
 ORDER BY sales_cnt_diff
 limit 100"""

        self.assertEqual(expected, _process_data(marked_sql, "balanced"))

    def test_sample_regular_comfortable(self):
        marked_sql = """WITH← all_sales AS(➕❌SELECT⚓ d.year ✖⚓,i.brand_id ✖⚓,i.class_id ✖⚓,i.category_id ✖⚓,i.manufact_id ✖⚓,SUM(➕sales_cnt➖) AS ⛓⚓sales_cnt ✖⚓,SUM(➕sales_amt➖) AS ⛓⚓sales_amt❌FROM⚓(➕SELECT⚓ d.year ✖⚓,i.brand_id ✖⚓,i.class_id ✖⚓,i.category_id ✖⚓,i.manufact_id ✖⚓,cs.quantity ⚫-⚫ COALESCE(➕cr.return_quantity✖⚓,0➖) AS ⛓⚓sales_cnt ✖⚓,cs.ext_sales_price ⚫-⚫ COALESCE(➕cr.return_amount✖⚓,0.0➖) AS ⛓⚓sales_amt ❌FROM⚓ catalog_sales cs ❌JOIN⚓ item i ❌ON⚓ i.item_sk ⚫=⚫ cs.item_sk ❌JOIN⚓ date_dim d ❌ON⚓ d.date_sk ⚫=⚫ cs.sold_date_sk ❌LEFT⚓ ❌JOIN⚓ catalog_returns cr ❌ON⚓(➕cs.order_number ⚫=⚫ cr.order_number ✖AND⚓ cs.item_sk ⚫=⚫ cr.item_sk➖) ❌WHERE⚓ i.category ⚫=⚫ 'Shoes' ❌UNION⚓❌ SELECT⚓ d.year ✖⚓,i.brand_id ✖⚓,i.class_id ✖⚓,i.category_id ✖⚓,i.manufact_id ✖⚓,ss.quantity ⚫-⚫ COALESCE(➕sr.return_quantity✖⚓,0➖) AS ⛓⚓sales_cnt ✖⚓,ss.ext_sales_price ⚫-⚫ COALESCE(➕sr.return_amt✖⚓,0.0➖) AS ⛓⚓sales_amt ❌FROM⚓ store_sales ss ❌JOIN⚓ item i ❌ON⚓ i.item_sk ⚫=⚫ ss.item_sk ❌JOIN⚓ date_dim d ❌ON⚓ d.date_sk ⚫=⚫ ss.sold_date_sk ❌LEFT⚓ ❌JOIN⚓ store_returns sr ❌ON⚓(➕ss.ticket_number ⚫=⚫ sr.ticket_number ✖AND⚓ ss.item_sk ⚫=⚫ sr.item_sk➖) ❌WHERE⚓ i.category ⚫=⚫ 'Shoes' ❌UNION⚓❌ SELECT⚓ d.year ✖⚓,i.brand_id ✖⚓,i.class_id ✖⚓,i.category_id ✖⚓,i.manufact_id ✖⚓,ws.quantity ⚫-⚫ COALESCE(➕wr.return_quantity✖⚓,0➖) AS ⛓⚓sales_cnt ✖⚓,ws.ext_sales_price ⚫-⚫ COALESCE(➕wr.return_amt✖⚓,0.0➖) AS ⛓⚓sales_amt ❌FROM⚓ web_sales ws ❌JOIN⚓ item i ❌ON⚓ i.item_sk ⚫=⚫ ws.item_sk ❌JOIN⚓ date_dim d ❌ON⚓ d.date_sk ⚫=⚫ ws.sold_date_sk ❌LEFT⚓ ❌JOIN⚓ web_returns wr ❌ON⚓(➕ws.order_number ⚫=⚫ wr.order_number ✖AND⚓ ws.item_sk ⚫=⚫ wr.item_sk➖) ❌WHERE⚓ i.category ⚫=⚫ 'Shoes'➖) sales_detail ❌GROUP⚓ BY d.year✖⚓,i.brand_id✖⚓,i.class_id✖⚓,i.category_id✖⚓,i.manufact_id⛓⚓➖)❌SELECT⚓ prev_yr.d_year AS ⛓⚓prev_year ✖⚓,curr_yr.d_year AS ⛓⚓year ✖⚓,curr_yr.i_brand_id ✖⚓,curr_yr.i_class_id ✖⚓,curr_yr.i_category_id ✖⚓,curr_yr.i_manufact_id ✖⚓,prev_yr.sales_cnt AS ⛓⚓prev_yr_cnt ✖⚓,curr_yr.sales_cnt AS ⛓⚓curr_yr_cnt ✖⚓,curr_yr.sales_cnt ⚫-⚫ prev_yr.sales_cnt AS ⛓⚓sales_cnt_diff ✖⚓,curr_yr.sales_amt ⚫-⚫ prev_yr.sales_amt AS ⛓⚓sales_amt_diff❌FROM⚓ all_sales curr_yr✖⚓,all_sales prev_yr❌WHERE⚓ curr_yr.brand_id ⚫=⚫ prev_yr.brand_id ✖AND⚓ curr_yr.class_id ⚫=⚫ prev_yr.class_id ✖AND⚓ curr_yr.category_id ⚫=⚫ prev_yr.category_id ✖AND⚓ curr_yr.manufact_id ⚫=⚫ prev_yr.manufact_id ✖AND⚓ curr_yr.year ⚫=⚫ 2000 ✖AND⚓ prev_yr.year ⚫=⚫ 2000 ⚫-⚫ 1 ✖AND⚓ CAST(➕curr_yr.sales_cnt AS DECIMAL(➕17✖⚓,2➖)➖) ⚫/⚫ CAST(➕prev_yr.sales_cnt AS DECIMAL(➕17✖⚓,2➖)➖) ⚫<⚫ 0.9❌ORDER⚓ BY sales_cnt_diff❌limit⚓ 100"""

        expected = """WITH all_sales AS(
    SELECT d.year 
          ,i.brand_id 
          ,i.class_id 
          ,i.category_id 
          ,i.manufact_id 
          ,SUM(sales_cnt) AS 
          sales_cnt 
          ,SUM(sales_amt) AS 
          sales_amt
      FROM(SELECT d.year 
                 ,i.brand_id 
                 ,i.class_id 
                 ,i.category_id 
                 ,i.manufact_id 
                 ,cs.quantity - COALESCE(cr.return_quantity
                  ,0) AS 
                 sales_cnt 
                 ,cs.ext_sales_price - COALESCE(cr.return_amount
                  ,0.0) AS 
                 sales_amt 
             FROM catalog_sales cs 
             JOIN item i 
               ON i.item_sk = cs.item_sk
             JOIN date_dim d 
               ON d.date_sk = cs.sold_date_sk
             LEFT 
             JOIN catalog_returns cr 
               ON(cs.order_number = cr.order_number
               AND cs.item_sk = cr.item_sk)
            WHERE i.category = 'Shoes'
            UNION
           SELECT d.year 
                 ,i.brand_id 
                 ,i.class_id 
                 ,i.category_id 
                 ,i.manufact_id 
                 ,ss.quantity - COALESCE(sr.return_quantity
                  ,0) AS 
                 sales_cnt 
                 ,ss.ext_sales_price - COALESCE(sr.return_amt
                  ,0.0) AS 
                 sales_amt 
             FROM store_sales ss 
             JOIN item i 
               ON i.item_sk = ss.item_sk
             JOIN date_dim d 
               ON d.date_sk = ss.sold_date_sk
             LEFT 
             JOIN store_returns sr 
               ON(ss.ticket_number = sr.ticket_number
               AND ss.item_sk = sr.item_sk)
            WHERE i.category = 'Shoes'
            UNION
           SELECT d.year 
                 ,i.brand_id 
                 ,i.class_id 
                 ,i.category_id 
                 ,i.manufact_id 
                 ,ws.quantity - COALESCE(wr.return_quantity
                  ,0) AS 
                 sales_cnt 
                 ,ws.ext_sales_price - COALESCE(wr.return_amt
                  ,0.0) AS 
                 sales_amt 
             FROM web_sales ws 
             JOIN item i 
               ON i.item_sk = ws.item_sk
             JOIN date_dim d 
               ON d.date_sk = ws.sold_date_sk
             LEFT 
             JOIN web_returns wr 
               ON(ws.order_number = wr.order_number
               AND ws.item_sk = wr.item_sk)
            WHERE i.category = 'Shoes') sales_detail
     GROUP BY d.year
          ,i.brand_id
          ,i.class_id
          ,i.category_id
          ,i.manufact_id
          )
SELECT prev_yr.d_year AS 
      prev_year 
      ,curr_yr.d_year AS 
      year 
      ,curr_yr.i_brand_id 
      ,curr_yr.i_class_id 
      ,curr_yr.i_category_id 
      ,curr_yr.i_manufact_id 
      ,prev_yr.sales_cnt AS 
      prev_yr_cnt 
      ,curr_yr.sales_cnt AS 
      curr_yr_cnt 
      ,curr_yr.sales_cnt - prev_yr.sales_cnt AS
      sales_cnt_diff 
      ,curr_yr.sales_amt - prev_yr.sales_amt AS
      sales_amt_diff
  FROM all_sales curr_yr
      ,all_sales prev_yr
 WHERE curr_yr.brand_id = prev_yr.brand_id
   AND curr_yr.class_id = prev_yr.class_id
   AND curr_yr.category_id = prev_yr.category_id
   AND curr_yr.manufact_id = prev_yr.manufact_id
   AND curr_yr.year = 2000
   AND prev_yr.year = 2000 - 1
   AND CAST(curr_yr.sales_cnt AS DECIMAL(17
                 ,2)) / CAST(prev_yr.sales_cnt AS DECIMAL(17
                 ,2)) < 0.9
 ORDER BY sales_cnt_diff
 limit 100"""

        self.assertEqual(expected, _process_data(marked_sql, "comfortable"))

    def test_sample_simple_comfortable(self):
        marked_sql = """SELECT⚓ p1✖⚓,p2✖⚓,count(➕*➖) as ⛓⚓numorders❌FROM⚓(➕SELECT⚓ op1.OrderID✖⚓,op1.ProductID as ⛓⚓p1✖⚓,op2.ProductID as ⛓⚓p2 ❌FROM⚓(➕SELECT⚓ DISTINCT OrderID✖⚓,ProductID ❌FROM⚓ OrderLines➖)op1 ❌JOIN⚓(➕SELECT⚓ DISTINCT OrderID✖⚓,ProductID ❌FROM⚓ OrderLines➖)op2 ❌ON⚓ op1.OrderID ⚫=⚫ op2.OrderID ✖AND⚓ op1.ProductID ⚫>⚫ op2.ProductID➖)combinations❌GROUP⚓ BY p1✖⚓,p2"""

        expected = """SELECT p1
      ,p2
      ,count(*) as 
      numorders
  FROM(SELECT op1.OrderID
             ,op1.ProductID as 
             p1
             ,op2.ProductID as 
             p2 
         FROM(SELECT DISTINCT OrderID
                    ,ProductID 
                FROM OrderLines)op1 
         JOIN(SELECT DISTINCT OrderID
                    ,ProductID 
                FROM OrderLines)op2 
           ON op1.OrderID = op2.OrderID
          AND op1.ProductID > op2.ProductID)combinations
 GROUP BY p1
      ,p2"""

        self.assertEqual(expected, _process_data(marked_sql, "comfortable"))

    def test_sample_simple_compact(self):
        marked_sql = """SELECT⚓ p1✖⚓,p2✖⚓,count(➕*➖) as ⛓⚓numorders❌FROM⚓(➕SELECT⚓ op1.OrderID✖⚓,op1.ProductID as ⛓⚓p1✖⚓,op2.ProductID as ⛓⚓p2 ❌FROM⚓(➕SELECT⚓ DISTINCT OrderID✖⚓,ProductID ❌FROM⚓ OrderLines➖)op1 ❌JOIN⚓(➕SELECT⚓ DISTINCT OrderID✖⚓,ProductID ❌FROM⚓ OrderLines➖)op2 ❌ON⚓ op1.OrderID ⚫=⚫ op2.OrderID ✖AND⚓ op1.ProductID ⚫>⚫ op2.ProductID➖)combinations❌GROUP⚓ BY p1✖⚓,p2"""

        expected = """SELECT p1
      ,p2
      ,count(*) as numorders
  FROM(SELECT op1.OrderID
             ,op1.ProductID as p1
             ,op2.ProductID as p2 
         FROM(SELECT DISTINCT OrderID
                    ,ProductID 
                FROM OrderLines)op1 
         JOIN(SELECT DISTINCT OrderID
                    ,ProductID 
                FROM OrderLines)op2 
           ON op1.OrderID=op2.OrderID
          AND op1.ProductID>op2.ProductID)combinations
 GROUP BY p1
      ,p2"""

        self.assertEqual(expected, _process_data(marked_sql, "compact"))

    def test_sample_simple_balanced(self):
        marked_sql = """SELECT⚓ p1✖⚓,p2✖⚓,count(➕*➖) as ⛓⚓numorders❌FROM⚓(➕SELECT⚓ op1.OrderID✖⚓,op1.ProductID as ⛓⚓p1✖⚓,op2.ProductID as ⛓⚓p2 ❌FROM⚓(➕SELECT⚓ DISTINCT OrderID✖⚓,ProductID ❌FROM⚓ OrderLines➖)op1 ❌JOIN⚓(➕SELECT⚓ DISTINCT OrderID✖⚓,ProductID ❌FROM⚓ OrderLines➖)op2 ❌ON⚓ op1.OrderID ⚫=⚫ op2.OrderID ✖AND⚓ op1.ProductID ⚫>⚫ op2.ProductID➖)combinations❌GROUP⚓ BY p1✖⚓,p2"""

        expected = """SELECT p1
      ,p2
      ,count(*) as numorders
  FROM(SELECT op1.OrderID
             ,op1.ProductID as p1
             ,op2.ProductID as p2 
         FROM(SELECT DISTINCT OrderID
                    ,ProductID 
                FROM OrderLines)op1 
         JOIN(SELECT DISTINCT OrderID
                    ,ProductID 
                FROM OrderLines)op2 
           ON op1.OrderID = op2.OrderID
          AND op1.ProductID > op2.ProductID)combinations
 GROUP BY p1
      ,p2"""

        self.assertEqual(expected, _process_data(marked_sql, "balanced"))

    def test_sample_complex_balanced(self):
        marked_sql = """WITH← date_list AS(➕❌ SELECT⚓ CAST(➕'2021-05-24' AS date➖) AS ⛓⚓OrderDate ❌UNION⚓❌ SELECT⚓ CAST(➕'2021-05-25' AS date➖) AS ⛓⚓OrderDate⛓⚓➖)❌,unique_orderedouters AS(➕❌ select⚓ PURCHASEORDERLINEID✖⚓,ORDEREDOUTERS✖⚓,dl.OrderDate ❌from⚓ PURCHASING_PURCHASEORDERLINES a ❌JOIN⚓ date_list dl ❌ON⚓ a.LASTRECEIPTDATE ⚫<=⚫ OrderDate ✖AND⚓(➕ a.LASTEDITEDWHEN ⚫>⚫ OrderDate ✖OR⚓ a.LASTEDITEDWHEN is NULL➖) ❌where⚓ a.PURCHASEORDERID ⚫=⚫ 27229 ✖and⚓ a.STOCKITEMID ⚫=⚫ 1 ❌QUALIFY⚓ ROW_NUMBER(➕➖) OVER(➕ PARTITION⧆ BY ORDEREDOUTERS ❌ORDER⚓⧆ BY RECEIVEDOUTERS DESC➖) ⚫=⚫ 1⛓⚓➖)❌,unique_purchase as(➕❌ select⚓ STOCKITEMID✖⚓,ORDEREDOUTERS✖⚓,dl.OrderDate ❌from⚓ PURCHASING_PURCHASEORDERLINES a ❌JOIN⚓ date_list dl ❌ON⚓ a.LASTRECEIPTDATE ⚫<=⚫ OrderDate ✖AND⚓(➕ a.LASTEDITEDWHEN ⚫>⚫ OrderDate ✖OR⚓ a.LASTEDITEDWHEN is NULL➖) ❌where⚓ a.PURCHASEORDERID ⚫=⚫ 27033 ✖and⚓ a.STOCKITEMID ⚫=⚫ 1 ❌QUALIFY⚓ ROW_NUMBER(➕➖) OVER(➕ PARTITION⧆ BY ORDEREDOUTERS ❌ORDER⚓⧆ BY RECEIVEDOUTERS DESC➖) ⚫=⚫ 1⛓⚓➖)❌,unique_item as(➕❌ select⚓ STOCKITEMID✖⚓,ORDEREDOUTERS✖⚓,dl.OrderDate ❌from⚓ PURCHASING_PURCHASEORDERLINES a ❌JOIN⚓ date_list dl ❌ON⚓ a.LASTRECEIPTDATE ⚫<=⚫ OrderDate ✖AND⚓(➕ a.LASTEDITEDWHEN ⚫>⚫ OrderDate ✖OR⚓ a.LASTEDITEDWHEN is NULL➖) ❌where⚓ a.PURCHASEORDERID ⚫=⚫ 114364 ✖and⚓ a.STOCKITEMID ⚫=⚫ 1 ❌QUALIFY⚓ ROW_NUMBER(➕➖) OVER(➕ PARTITION⧆ BY ORDEREDOUTERS ❌ORDER⚓⧆ BY RECEIVEDOUTERS DESC➖) ⚫=⚫ 1⛓⚓➖)❌,unique_parent as(➕❌ select⚓ STOCKITEMID✖⚓,ORDEREDOUTERS✖⚓,dl.OrderDate ❌from⚓ PURCHASING_PURCHASEORDERLINES a ❌JOIN⚓ date_list dl ❌ON⚓ a.LASTRECEIPTDATE ⚫<=⚫ OrderDate ✖AND⚓(➕ a.LASTEDITEDWHEN ⚫>⚫ OrderDate ✖OR⚓ a.LASTEDITEDWHEN is NULL➖) ❌where⚓ a.PURCHASEORDERID ⚫=⚫ 34559 ✖and⚓ a.STOCKITEMID ⚫=⚫ 1 ❌QUALIFY⚓ ROW_NUMBER(➕➖) OVER(➕ PARTITION⧆ BY ORDEREDOUTERS ❌ORDER⚓⧆ BY RECEIVEDOUTERS DESC➖) ⚫=⚫ 1⛓⚓➖)❌,purchase_con AS(➕❌ select⚓ DISTINCT CONCAT(➕pol.ORDEREDOUTERS✖⚓,'-0'➖) as ⛓⚓ID✖⚓,dl.OrderDate as ⛓⚓search_date✖⚓,pol.ORDEREDOUTERS as ⛓⚓orderedouters✖⚓,sinv.ORDERID✖⚓,sct.PAYMENTMETHODID✖⚓,sct.TRANSACTIONDATE✖⚓,up.PURCHASEORDERLINEID as ⛓⚓PolID✖⚓,ui.ORDEREDOUTERS as ⛓⚓outersid✖⚓,UPPER(➕up.ORDEREDOUTERS➖) as ⛓⚓outersname✖⚓,sinvl.STOCKITEMID✖⚓,0 as ⛓⚓ParentLevel✖⚓,'Direct Issuer of the Voucher' as ⛓⚓ParentLevel_Desc ❌from⚓ PURCHASING_PURCHASEORDERLINES pol ❌inner⚓ ❌join⚓ SALES_ORDERS sord ❌on⚓ sord.ORDERID ⚫=⚫ pol.PURCHASEORDERID ✖and⚓ pol.PURCHASEORDERID ⚫=⚫ 35 ✖and⚓ pol.STOCKITEMID ⚫=⚫ 1 ✖and⚓ sord.SALESPERSONPERSONID ⚫=⚫ 1 ✖and⚓ sord.CONTACTPERSONID⚫=⚫ 1 ✖and⚓ sord.DELIVERYINSTRUCTIONS ⚫=⚫ 'SHR' ✖AND⚓ pol.ORDEREDOUTERS IS NOT NULL ✖AND⚓ sord.CUSTOMERPURCHASEORDERNUMBER is not null ❌inner⚓ ❌join⚓ SALES_INVOICES sinv ❌on⚓ sinv.ORDERID ⚫=⚫ sord.ORDERID ❌INNER⚓ ❌JOIN⚓ SALES_CUSTOMERS AS scus ❌ON⚓ scus.CUSTOMERID ⚫=⚫ sinv.CUSTOMERID ❌INNER⚓ ❌JOIN⚓ SALES_CUSTOMERTRANSACTIONS AS sct ❌ON⚓ sct.CUSTOMERID ⚫=⚫ scus.CUSTOMERID ❌INNER⚓ ❌JOIN⚓ SALES_INVOICELINES AS sinvl ❌ON⚓ sinvl.INVOICEID ⚫=⚫ sct.INVOICEID ❌INNER⚓ ❌join⚓ unique_purchase up ❌on⚓ ui.STOCKITEMID ⚫=⚫ sinvl.STOCKITEMID ❌LEFT⚓ ❌join⚓ unique_item ui ❌on⚓ ui.STOCKITEMID ⚫=⚫ sinvl.STOCKITEMID ❌INNER⚓ ❌JOIN⚓ date_list dl ❌ON⚓ pol.LASTRECEIPTDATE⚫<=⚫ dl.OrderDate ✖AND⚓(➕ pol.LASTEDITEDWHEN ⚫>⚫ dl.OrderDate ✖OR⚓ pol.LASTEDITEDWHEN is NULL➖) ✖AND⚓ sinv.INVOICEDATE ⚫<=⚫ dl.OrderDate ✖AND⚓(➕ sinv.LASTEDITEDWHEN ⚫>⚫ dl.OrderDate ✖OR⚓ sinv.LASTEDITEDWHEN is NULL➖) ❌where⚓ pol.STOCKITEMID ⚫=⚫ 35 ✖and⚓ pol.STOCKITEMID ⚫=⚫ 1 ✖AND⚓ pol.ORDEREDOUTERS IS NOT NULL ✖and⚓ sord.SALESPERSONPERSONID ⚫=⚫ 1 ✖and⚓ sord.CONTACTPERSONID⚫=⚫ 1 ✖and⚓ sord.DELIVERYINSTRUCTIONS ⚫=⚫ 'SHR' ✖AND⚓ sord.CUSTOMERPURCHASEORDERNUMBER is not null⛓⚓➖)❌,rule AS(➕❌ select⚓ distinct CONCAT(➕orderedouters.ORDEREDOUTERS✖⚓,'-0'➖) as ⛓⚓ID✖⚓,orderedouters.OrderDate as ⛓⚓search_date✖⚓,orderedouters.ORDEREDOUTERS as ⛓⚓orderedouters✖⚓,sct.PAYMENTMETHODID✖⚓,sct.TRANSACTIONDATE✖⚓,up.PURCHASEORDERLINEID as ⛓⚓PolID✖⚓,ui.ORDEREDOUTERS as ⛓⚓outersid✖⚓,UPPER(➕up.ORDEREDOUTERS➖) as ⛓⚓outersname✖⚓,sinvl.STOCKITEMID✖⚓,0 as ⛓⚓ParentLevel✖⚓,'Direct Issuer of Salesperson' as ⛓⚓ParentLevel_Desc ❌from⚓ unique_orderedouters orderedouters ❌inner⚓ ❌join⚓ SALES_CUSTOMERTRANSACTIONS sct ❌on⚓ orderedouters.PURCHASEORDERLINEID ⚫=⚫ sct.PURCHASEORDERLINEID ❌inner⚓ ❌join⚓ SALES_INVOICELINES sinvl ❌on⚓ sinvl.INVOICEID ⚫=⚫ sct.INVOICEID ❌inner⚓ ❌join⚓ unique_purchase up ❌on⚓ up.PURCHASEORDERLINEID ⚫=⚫ sinvl.PURCHASEORDERLINEID ❌LEFT⚓ ❌join⚓ unique_item up ❌on⚓ ui.PURCHASEORDERLINEID ⚫=⚫ sinvl.PURCHASEORDERLINEID ✖and⚓ ui.OrderDate ⚫=⚫ orderedouters.OrderDate ❌where⚓ sct.ISFINALIZED in(➕'TRUE'➖)⛓⚓➖)❌,direct_map AS(➕❌ select⚓ ID✖⚓,search_date✖⚓,orderedouters✖⚓,PAYMENTMETHODID✖⚓,TRANSACTIONDATE✖⚓,PolID✖⚓,outersid✖⚓,outersname✖⚓,STOCKITEMID✖⚓,ParentLevel✖⚓,ParentLevel_Desc ❌from⚓ purchase_con ❌UNION⚓❌ select⚓ ID✖⚓,search_date✖⚓,orderedouters✖⚓,PAYMENTMETHODID✖⚓,TRANSACTIONDATE✖⚓,PolID✖⚓,outersid✖⚓,outersname✖⚓,STOCKITEMID✖⚓,ParentLevel✖⚓,ParentLevel_Desc ❌from⚓ rule ❌where⚓ ID not in(➕ select⚓ distinct ID ❌from⚓ purchase_con➖)⛓⚓➖)❌,parent_child AS(➕❌ select⚓ Distinct upar.OrderDate AS ⛓⚓search_date✖⚓,upar.STOCKITEMIDas ⛓⚓PolID✖⚓,UPPER(➕cls.ORDEREDOUTERS➖) as ⛓⚓outersname✖⚓,cln.ORDEREDOUTERS as ⛓⚓outersid✖⚓,upar.ORDEREDOUTERS as ⛓⚓parent_PolID✖⚓,UPPER(➕pls.ORDEREDOUTERS➖) as ⛓⚓parent_outersname✖⚓,pln.ORDEREDOUTERS as ⛓⚓parent_outersid ❌from⚓ unique_parent upar ❌left⚓ ❌join⚓ unique_purchase uprc ❌on⚓ uprc.STOCKITEMID ⚫=⚫ upar.STOCKITEMID ✖and⚓ uprc.OrderDate ⚫=⚫ upar.OrderDate ❌left⚓ ❌join⚓ unique_purchase uprcs ❌on⚓ pls.STOCKITEMID ⚫=⚫ upar.ORDEREDOUTERS ✖and⚓ uprcs.OrderDate ⚫=⚫ upar.OrderDate ❌left⚓ ❌join⚓ unique_item uit ❌on⚓ cln.STOCKITEMID ⚫=⚫ upar.STOCKITEMID ✖and⚓ uit.OrderDate ⚫=⚫ upar.OrderDate ❌left⚓ ❌join⚓ unique_item uitem ❌on⚓ uitem.STOCKITEMID ⚫=⚫ upar.ORDEREDOUTERS ✖and⚓ uitem.OrderDate ⚫=⚫ upar.OrderDate⛓⚓➖)❌,navigate_hierarchy as(➕❌ SELECT⚓ search_date✖⚓,PolID✖⚓,outersid✖⚓,cast(➕outersname as varchar➖) as ⛓⚓outersname✖⚓,parent_PolID✖⚓,parent_outersid✖⚓,cast(➕parent_outersname as varchar➖) as ⛓⚓parent_outersname✖⚓,1 as ⛓⚓ParentLevel✖⚓,concat(➕ cast(➕outersname as varchar➖)✖⚓,' -> '✖⚓,cast(➕parent_outersname as varchar➖)➖) as ⛓⚓outersnameline ❌from⚓ parent_child ❌UNION ALL⚓❌ SELECT⚓ c.search_date✖⚓,c.PolID✖⚓,c.outersid✖⚓,cast(➕c.outersname as varchar➖) as ⛓⚓outersname✖⚓,p.parent_PolID✖⚓,p.parent_outersid✖⚓,cast(➕p.parent_outersname as varchar➖) as ⛓⚓parent_outersname✖⚓,p.ParentLevel ⚫+⚫ 1✖⚓,cast(➕ CONCAT(➕ cast(➕c.outersname as varchar➖)✖⚓,' -> '✖⚓,cast(➕p.outersnameline as varchar➖)➖) AS varchar➖) as ⛓⚓outersnameline ❌from⚓ parent_child C ❌join⚓ navigate_hierarchy p ❌on⚓ p.PolID ⚫=⚫ c.parent_PolID ✖AND⚓ c.PolID ⚫<>⚫ c.parent_PolID ✖and⚓ p.ParentLevel ⚫<=⚫ 40 ✖AND⚓ p.search_date ⚫=⚫ c.search_date ❌where⚓ p.ParentLevel ⚫<=⚫ 40⛓⚓➖)❌,TEST_OUTPUT AS(➕❌ select⚓ DISTINCT ID✖⚓,search_date✖⚓,orderedouters✖⚓,PAYMENTMETHODID✖⚓,TRANSACTIONDATE✖⚓,PolID✖⚓,outersid✖⚓,outersname✖⚓,STOCKITEMID✖⚓,ParentLevel✖⚓,ParentLevel_Desc✖⚓,PolID as ⛓⚓parent_PolID✖⚓,outersid as ⛓⚓parent_outersid✖⚓,outersname as ⛓⚓parent_outersname✖⚓,outersname as ⛓⚓outersnameline ❌from⚓ direct_mapping ❌UNION⚓❌ select⚓ CONCAT(➕dm.orderedouters✖⚓,'-'✖⚓,nh.Parentlevel➖) as ⛓⚓ID✖⚓,dm.search_date✖⚓,dm.orderedouters✖⚓,dm.PAYMENTMETHODID✖⚓,dm.TRANSACTIONDATE✖⚓,nh.PolID✖⚓,nh.outersid✖⚓,nh.outersname✖⚓,dm.STOCKITEMID✖⚓,nh.ParentLevel✖⚓,❌CASE⚓➕ ❌WHEN⚓ nh.ParentLevel ⚫=⚫ 1 ❌THEN⚓ 'Immediate Parent of Salesperson Issuer' ❌ELSE⚓ concat(➕ 'Higher Level Parent ('✖⚓,nh.ParentLevel✖⚓,') Levels above the Salesperson Issuer'➖) ➖❌END⚓ as ⛓⚓ParentLevel_Desc✖⚓,parent_PolID✖⚓,parent_outersid✖⚓,parent_outersname✖⚓,outersnameline as ⛓⚓outersnameline ❌from⚓ navigate_hierarchy nh ❌inner⚓ ❌join⚓ direct_map dm ❌on⚓ dm.PolID ⚫=⚫ nh.PolID⛓⚓➖)❌SELECT⚓ *❌FROM⚓ TEST_OUTPUT ❌group⚓ by search_date"""

        expected = """WITH date_list AS(
    SELECT CAST('2021-05-24' AS date) AS OrderDate 
     UNION
    SELECT CAST('2021-05-25' AS date) AS OrderDate)
,unique_orderedouters AS(
    select PURCHASEORDERLINEID
          ,ORDEREDOUTERS
          ,dl.OrderDate 
      from PURCHASING_PURCHASEORDERLINES a 
      JOIN date_list dl 
        ON a.LASTRECEIPTDATE <= OrderDate
       AND( a.LASTEDITEDWHEN > OrderDate
            OR a.LASTEDITEDWHEN is NULL) 
     where a.PURCHASEORDERID = 27229
       and a.STOCKITEMID = 1
   QUALIFY ROW_NUMBER() OVER( PARTITION BY ORDEREDOUTERS 
         ORDER BY RECEIVEDOUTERS DESC) = 1)
,unique_purchase as(
    select STOCKITEMID
          ,ORDEREDOUTERS
          ,dl.OrderDate 
      from PURCHASING_PURCHASEORDERLINES a 
      JOIN date_list dl 
        ON a.LASTRECEIPTDATE <= OrderDate
       AND( a.LASTEDITEDWHEN > OrderDate
            OR a.LASTEDITEDWHEN is NULL) 
     where a.PURCHASEORDERID = 27033
       and a.STOCKITEMID = 1
   QUALIFY ROW_NUMBER() OVER( PARTITION BY ORDEREDOUTERS 
         ORDER BY RECEIVEDOUTERS DESC) = 1)
,unique_item as(
    select STOCKITEMID
          ,ORDEREDOUTERS
          ,dl.OrderDate 
      from PURCHASING_PURCHASEORDERLINES a 
      JOIN date_list dl 
        ON a.LASTRECEIPTDATE <= OrderDate
       AND( a.LASTEDITEDWHEN > OrderDate
            OR a.LASTEDITEDWHEN is NULL) 
     where a.PURCHASEORDERID = 114364
       and a.STOCKITEMID = 1
   QUALIFY ROW_NUMBER() OVER( PARTITION BY ORDEREDOUTERS 
         ORDER BY RECEIVEDOUTERS DESC) = 1)
,unique_parent as(
    select STOCKITEMID
          ,ORDEREDOUTERS
          ,dl.OrderDate 
      from PURCHASING_PURCHASEORDERLINES a 
      JOIN date_list dl 
        ON a.LASTRECEIPTDATE <= OrderDate
       AND( a.LASTEDITEDWHEN > OrderDate
            OR a.LASTEDITEDWHEN is NULL) 
     where a.PURCHASEORDERID = 34559
       and a.STOCKITEMID = 1
   QUALIFY ROW_NUMBER() OVER( PARTITION BY ORDEREDOUTERS 
         ORDER BY RECEIVEDOUTERS DESC) = 1)
,purchase_con AS(
    select DISTINCT CONCAT(pol.ORDEREDOUTERS
              ,'-0') as ID
          ,dl.OrderDate as search_date
          ,pol.ORDEREDOUTERS as orderedouters
          ,sinv.ORDERID
          ,sct.PAYMENTMETHODID
          ,sct.TRANSACTIONDATE
          ,up.PURCHASEORDERLINEID as PolID
          ,ui.ORDEREDOUTERS as outersid
          ,UPPER(up.ORDEREDOUTERS) as outersname
          ,sinvl.STOCKITEMID
          ,0 as ParentLevel
          ,'Direct Issuer of the Voucher' as ParentLevel_Desc 
      from PURCHASING_PURCHASEORDERLINES pol 
     inner 
      join SALES_ORDERS sord 
        on sord.ORDERID = pol.PURCHASEORDERID
       and pol.PURCHASEORDERID = 35
       and pol.STOCKITEMID = 1
       and sord.SALESPERSONPERSONID = 1
       and sord.CONTACTPERSONID = 1
       and sord.DELIVERYINSTRUCTIONS = 'SHR'
       AND pol.ORDEREDOUTERS IS NOT NULL 
       AND sord.CUSTOMERPURCHASEORDERNUMBER is not null 
     inner 
      join SALES_INVOICES sinv 
        on sinv.ORDERID = sord.ORDERID
     INNER 
      JOIN SALES_CUSTOMERS AS scus 
        ON scus.CUSTOMERID = sinv.CUSTOMERID
     INNER 
      JOIN SALES_CUSTOMERTRANSACTIONS AS sct 
        ON sct.CUSTOMERID = scus.CUSTOMERID
     INNER 
      JOIN SALES_INVOICELINES AS sinvl 
        ON sinvl.INVOICEID = sct.INVOICEID
     INNER 
      join unique_purchase up 
        on ui.STOCKITEMID = sinvl.STOCKITEMID
      LEFT 
      join unique_item ui 
        on ui.STOCKITEMID = sinvl.STOCKITEMID
     INNER 
      JOIN date_list dl 
        ON pol.LASTRECEIPTDATE <= dl.OrderDate
       AND( pol.LASTEDITEDWHEN > dl.OrderDate
            OR pol.LASTEDITEDWHEN is NULL) 
       AND sinv.INVOICEDATE <= dl.OrderDate
       AND( sinv.LASTEDITEDWHEN > dl.OrderDate
            OR sinv.LASTEDITEDWHEN is NULL) 
     where pol.STOCKITEMID = 35
       and pol.STOCKITEMID = 1
       AND pol.ORDEREDOUTERS IS NOT NULL 
       and sord.SALESPERSONPERSONID = 1
       and sord.CONTACTPERSONID = 1
       and sord.DELIVERYINSTRUCTIONS = 'SHR'
       AND sord.CUSTOMERPURCHASEORDERNUMBER is not null)
,rule AS(
    select distinct CONCAT(orderedouters.ORDEREDOUTERS
              ,'-0') as ID
          ,orderedouters.OrderDate as search_date
          ,orderedouters.ORDEREDOUTERS as orderedouters
          ,sct.PAYMENTMETHODID
          ,sct.TRANSACTIONDATE
          ,up.PURCHASEORDERLINEID as PolID
          ,ui.ORDEREDOUTERS as outersid
          ,UPPER(up.ORDEREDOUTERS) as outersname
          ,sinvl.STOCKITEMID
          ,0 as ParentLevel
          ,'Direct Issuer of Salesperson' as ParentLevel_Desc 
      from unique_orderedouters orderedouters 
     inner 
      join SALES_CUSTOMERTRANSACTIONS sct 
        on orderedouters.PURCHASEORDERLINEID = sct.PURCHASEORDERLINEID
     inner 
      join SALES_INVOICELINES sinvl 
        on sinvl.INVOICEID = sct.INVOICEID
     inner 
      join unique_purchase up 
        on up.PURCHASEORDERLINEID = sinvl.PURCHASEORDERLINEID
      LEFT 
      join unique_item up 
        on ui.PURCHASEORDERLINEID = sinvl.PURCHASEORDERLINEID
       and ui.OrderDate = orderedouters.OrderDate
     where sct.ISFINALIZED in('TRUE'))
,direct_map AS(
    select ID
          ,search_date
          ,orderedouters
          ,PAYMENTMETHODID
          ,TRANSACTIONDATE
          ,PolID
          ,outersid
          ,outersname
          ,STOCKITEMID
          ,ParentLevel
          ,ParentLevel_Desc 
      from purchase_con 
     UNION
    select ID
          ,search_date
          ,orderedouters
          ,PAYMENTMETHODID
          ,TRANSACTIONDATE
          ,PolID
          ,outersid
          ,outersname
          ,STOCKITEMID
          ,ParentLevel
          ,ParentLevel_Desc 
      from rule 
     where ID not in( select distinct ID 
                         from purchase_con))
,parent_child AS(
    select Distinct upar.OrderDate AS search_date
          ,upar.STOCKITEMIDas PolID
          ,UPPER(cls.ORDEREDOUTERS) as outersname
          ,cln.ORDEREDOUTERS as outersid
          ,upar.ORDEREDOUTERS as parent_PolID
          ,UPPER(pls.ORDEREDOUTERS) as parent_outersname
          ,pln.ORDEREDOUTERS as parent_outersid 
      from unique_parent upar 
      left 
      join unique_purchase uprc 
        on uprc.STOCKITEMID = upar.STOCKITEMID
       and uprc.OrderDate = upar.OrderDate
      left 
      join unique_purchase uprcs 
        on pls.STOCKITEMID = upar.ORDEREDOUTERS
       and uprcs.OrderDate = upar.OrderDate
      left 
      join unique_item uit 
        on cln.STOCKITEMID = upar.STOCKITEMID
       and uit.OrderDate = upar.OrderDate
      left 
      join unique_item uitem 
        on uitem.STOCKITEMID = upar.ORDEREDOUTERS
       and uitem.OrderDate = upar.OrderDate)
,navigate_hierarchy as(
    SELECT search_date
          ,PolID
          ,outersid
          ,cast(outersname as varchar) as outersname
          ,parent_PolID
          ,parent_outersid
          ,cast(parent_outersname as varchar) as parent_outersname
          ,1 as ParentLevel
          ,concat( cast(outersname as varchar)
                             ,' -> '
                             ,cast(parent_outersname as varchar)) as outersnameline 
      from parent_child 
   UNION ALL
    SELECT c.search_date
          ,c.PolID
          ,c.outersid
          ,cast(c.outersname as varchar) as outersname
          ,p.parent_PolID
          ,p.parent_outersid
          ,cast(p.parent_outersname as varchar) as parent_outersname
          ,p.ParentLevel + 1
          ,cast( CONCAT( cast(c.outersname as varchar)
                  ,' -> '
                  ,cast(p.outersnameline as varchar)) AS varchar) as outersnameline 
      from parent_child C 
      join navigate_hierarchy p 
        on p.PolID = c.parent_PolID
       AND c.PolID <> c.parent_PolID
       and p.ParentLevel <= 40
       AND p.search_date = c.search_date
     where p.ParentLevel <= 40)
,TEST_OUTPUT AS(
    select DISTINCT ID
          ,search_date
          ,orderedouters
          ,PAYMENTMETHODID
          ,TRANSACTIONDATE
          ,PolID
          ,outersid
          ,outersname
          ,STOCKITEMID
          ,ParentLevel
          ,ParentLevel_Desc
          ,PolID as parent_PolID
          ,outersid as parent_outersid
          ,outersname as parent_outersname
          ,outersname as outersnameline 
      from direct_mapping 
     UNION
    select CONCAT(dm.orderedouters
                             ,'-'
                             ,nh.Parentlevel) as ID
          ,dm.search_date
          ,dm.orderedouters
          ,dm.PAYMENTMETHODID
          ,dm.TRANSACTIONDATE
          ,nh.PolID
          ,nh.outersid
          ,nh.outersname
          ,dm.STOCKITEMID
          ,nh.ParentLevel
          ,
      CASE 
                         WHEN nh.ParentLevel = 1
                         THEN 'Immediate Parent of Salesperson Issuer' 
                         ELSE concat( 'Higher Level Parent ('
                  ,nh.ParentLevel
                  ,') Levels above the Salesperson Issuer') 
       END as ParentLevel_Desc
          ,parent_PolID
          ,parent_outersid
          ,parent_outersname
          ,outersnameline as outersnameline 
      from navigate_hierarchy nh 
     inner 
      join direct_map dm 
        on dm.PolID = nh.PolID)
SELECT *
  FROM TEST_OUTPUT 
 group by search_date"""

        self.assertEqual(expected, _process_data(marked_sql, "balanced"))

    def test_sample_complex_comfortable(self):
        marked_sql = """WITH← date_list AS(➕❌ SELECT⚓ CAST(➕'2021-05-24' AS date➖) AS ⛓⚓OrderDate ❌UNION⚓❌ SELECT⚓ CAST(➕'2021-05-25' AS date➖) AS ⛓⚓OrderDate⛓⚓➖)❌,unique_orderedouters AS(➕❌ select⚓ PURCHASEORDERLINEID✖⚓,ORDEREDOUTERS✖⚓,dl.OrderDate ❌from⚓ PURCHASING_PURCHASEORDERLINES a ❌JOIN⚓ date_list dl ❌ON⚓ a.LASTRECEIPTDATE ⚫<=⚫ OrderDate ✖AND⚓(➕ a.LASTEDITEDWHEN ⚫>⚫ OrderDate ✖OR⚓ a.LASTEDITEDWHEN is NULL➖) ❌where⚓ a.PURCHASEORDERID ⚫=⚫ 27229 ✖and⚓ a.STOCKITEMID ⚫=⚫ 1 ❌QUALIFY⚓ ROW_NUMBER(➕➖) OVER(➕ PARTITION⧆ BY ORDEREDOUTERS ❌ORDER⚓⧆ BY RECEIVEDOUTERS DESC➖) ⚫=⚫ 1⛓⚓➖)❌,unique_purchase as(➕❌ select⚓ STOCKITEMID✖⚓,ORDEREDOUTERS✖⚓,dl.OrderDate ❌from⚓ PURCHASING_PURCHASEORDERLINES a ❌JOIN⚓ date_list dl ❌ON⚓ a.LASTRECEIPTDATE ⚫<=⚫ OrderDate ✖AND⚓(➕ a.LASTEDITEDWHEN ⚫>⚫ OrderDate ✖OR⚓ a.LASTEDITEDWHEN is NULL➖) ❌where⚓ a.PURCHASEORDERID ⚫=⚫ 27033 ✖and⚓ a.STOCKITEMID ⚫=⚫ 1 ❌QUALIFY⚓ ROW_NUMBER(➕➖) OVER(➕ PARTITION⧆ BY ORDEREDOUTERS ❌ORDER⚓⧆ BY RECEIVEDOUTERS DESC➖) ⚫=⚫ 1⛓⚓➖)❌,unique_item as(➕❌ select⚓ STOCKITEMID✖⚓,ORDEREDOUTERS✖⚓,dl.OrderDate ❌from⚓ PURCHASING_PURCHASEORDERLINES a ❌JOIN⚓ date_list dl ❌ON⚓ a.LASTRECEIPTDATE ⚫<=⚫ OrderDate ✖AND⚓(➕ a.LASTEDITEDWHEN ⚫>⚫ OrderDate ✖OR⚓ a.LASTEDITEDWHEN is NULL➖) ❌where⚓ a.PURCHASEORDERID ⚫=⚫ 114364 ✖and⚓ a.STOCKITEMID ⚫=⚫ 1 ❌QUALIFY⚓ ROW_NUMBER(➕➖) OVER(➕ PARTITION⧆ BY ORDEREDOUTERS ❌ORDER⚓⧆ BY RECEIVEDOUTERS DESC➖) ⚫=⚫ 1⛓⚓➖)❌,unique_parent as(➕❌ select⚓ STOCKITEMID✖⚓,ORDEREDOUTERS✖⚓,dl.OrderDate ❌from⚓ PURCHASING_PURCHASEORDERLINES a ❌JOIN⚓ date_list dl ❌ON⚓ a.LASTRECEIPTDATE ⚫<=⚫ OrderDate ✖AND⚓(➕ a.LASTEDITEDWHEN ⚫>⚫ OrderDate ✖OR⚓ a.LASTEDITEDWHEN is NULL➖) ❌where⚓ a.PURCHASEORDERID ⚫=⚫ 34559 ✖and⚓ a.STOCKITEMID ⚫=⚫ 1 ❌QUALIFY⚓ ROW_NUMBER(➕➖) OVER(➕ PARTITION⧆ BY ORDEREDOUTERS ❌ORDER⚓⧆ BY RECEIVEDOUTERS DESC➖) ⚫=⚫ 1⛓⚓➖)❌,purchase_con AS(➕❌ select⚓ DISTINCT CONCAT(➕pol.ORDEREDOUTERS✖⚓,'-0'➖) as ⛓⚓ID✖⚓,dl.OrderDate as ⛓⚓search_date✖⚓,pol.ORDEREDOUTERS as ⛓⚓orderedouters✖⚓,sinv.ORDERID✖⚓,sct.PAYMENTMETHODID✖⚓,sct.TRANSACTIONDATE✖⚓,up.PURCHASEORDERLINEID as ⛓⚓PolID✖⚓,ui.ORDEREDOUTERS as ⛓⚓outersid✖⚓,UPPER(➕up.ORDEREDOUTERS➖) as ⛓⚓outersname✖⚓,sinvl.STOCKITEMID✖⚓,0 as ⛓⚓ParentLevel✖⚓,'Direct Issuer of the Voucher' as ⛓⚓ParentLevel_Desc ❌from⚓ PURCHASING_PURCHASEORDERLINES pol ❌inner⚓ ❌join⚓ SALES_ORDERS sord ❌on⚓ sord.ORDERID ⚫=⚫ pol.PURCHASEORDERID ✖and⚓ pol.PURCHASEORDERID ⚫=⚫ 35 ✖and⚓ pol.STOCKITEMID ⚫=⚫ 1 ✖and⚓ sord.SALESPERSONPERSONID ⚫=⚫ 1 ✖and⚓ sord.CONTACTPERSONID⚫=⚫ 1 ✖and⚓ sord.DELIVERYINSTRUCTIONS ⚫=⚫ 'SHR' ✖AND⚓ pol.ORDEREDOUTERS IS NOT NULL ✖AND⚓ sord.CUSTOMERPURCHASEORDERNUMBER is not null ❌inner⚓ ❌join⚓ SALES_INVOICES sinv ❌on⚓ sinv.ORDERID ⚫=⚫ sord.ORDERID ❌INNER⚓ ❌JOIN⚓ SALES_CUSTOMERS AS scus ❌ON⚓ scus.CUSTOMERID ⚫=⚫ sinv.CUSTOMERID ❌INNER⚓ ❌JOIN⚓ SALES_CUSTOMERTRANSACTIONS AS sct ❌ON⚓ sct.CUSTOMERID ⚫=⚫ scus.CUSTOMERID ❌INNER⚓ ❌JOIN⚓ SALES_INVOICELINES AS sinvl ❌ON⚓ sinvl.INVOICEID ⚫=⚫ sct.INVOICEID ❌INNER⚓ ❌join⚓ unique_purchase up ❌on⚓ ui.STOCKITEMID ⚫=⚫ sinvl.STOCKITEMID ❌LEFT⚓ ❌join⚓ unique_item ui ❌on⚓ ui.STOCKITEMID ⚫=⚫ sinvl.STOCKITEMID ❌INNER⚓ ❌JOIN⚓ date_list dl ❌ON⚓ pol.LASTRECEIPTDATE⚫<=⚫ dl.OrderDate ✖AND⚓(➕ pol.LASTEDITEDWHEN ⚫>⚫ dl.OrderDate ✖OR⚓ pol.LASTEDITEDWHEN is NULL➖) ✖AND⚓ sinv.INVOICEDATE ⚫<=⚫ dl.OrderDate ✖AND⚓(➕ sinv.LASTEDITEDWHEN ⚫>⚫ dl.OrderDate ✖OR⚓ sinv.LASTEDITEDWHEN is NULL➖) ❌where⚓ pol.STOCKITEMID ⚫=⚫ 35 ✖and⚓ pol.STOCKITEMID ⚫=⚫ 1 ✖AND⚓ pol.ORDEREDOUTERS IS NOT NULL ✖and⚓ sord.SALESPERSONPERSONID ⚫=⚫ 1 ✖and⚓ sord.CONTACTPERSONID⚫=⚫ 1 ✖and⚓ sord.DELIVERYINSTRUCTIONS ⚫=⚫ 'SHR' ✖AND⚓ sord.CUSTOMERPURCHASEORDERNUMBER is not null⛓⚓➖)❌,rule AS(➕❌ select⚓ distinct CONCAT(➕orderedouters.ORDEREDOUTERS✖⚓,'-0'➖) as ⛓⚓ID✖⚓,orderedouters.OrderDate as ⛓⚓search_date✖⚓,orderedouters.ORDEREDOUTERS as ⛓⚓orderedouters✖⚓,sct.PAYMENTMETHODID✖⚓,sct.TRANSACTIONDATE✖⚓,up.PURCHASEORDERLINEID as ⛓⚓PolID✖⚓,ui.ORDEREDOUTERS as ⛓⚓outersid✖⚓,UPPER(➕up.ORDEREDOUTERS➖) as ⛓⚓outersname✖⚓,sinvl.STOCKITEMID✖⚓,0 as ⛓⚓ParentLevel✖⚓,'Direct Issuer of Salesperson' as ⛓⚓ParentLevel_Desc ❌from⚓ unique_orderedouters orderedouters ❌inner⚓ ❌join⚓ SALES_CUSTOMERTRANSACTIONS sct ❌on⚓ orderedouters.PURCHASEORDERLINEID ⚫=⚫ sct.PURCHASEORDERLINEID ❌inner⚓ ❌join⚓ SALES_INVOICELINES sinvl ❌on⚓ sinvl.INVOICEID ⚫=⚫ sct.INVOICEID ❌inner⚓ ❌join⚓ unique_purchase up ❌on⚓ up.PURCHASEORDERLINEID ⚫=⚫ sinvl.PURCHASEORDERLINEID ❌LEFT⚓ ❌join⚓ unique_item up ❌on⚓ ui.PURCHASEORDERLINEID ⚫=⚫ sinvl.PURCHASEORDERLINEID ✖and⚓ ui.OrderDate ⚫=⚫ orderedouters.OrderDate ❌where⚓ sct.ISFINALIZED in(➕'TRUE'➖)⛓⚓➖)❌,direct_map AS(➕❌ select⚓ ID✖⚓,search_date✖⚓,orderedouters✖⚓,PAYMENTMETHODID✖⚓,TRANSACTIONDATE✖⚓,PolID✖⚓,outersid✖⚓,outersname✖⚓,STOCKITEMID✖⚓,ParentLevel✖⚓,ParentLevel_Desc ❌from⚓ purchase_con ❌UNION⚓❌ select⚓ ID✖⚓,search_date✖⚓,orderedouters✖⚓,PAYMENTMETHODID✖⚓,TRANSACTIONDATE✖⚓,PolID✖⚓,outersid✖⚓,outersname✖⚓,STOCKITEMID✖⚓,ParentLevel✖⚓,ParentLevel_Desc ❌from⚓ rule ❌where⚓ ID not in(➕ select⚓ distinct ID ❌from⚓ purchase_con➖)⛓⚓➖)❌,parent_child AS(➕❌ select⚓ Distinct upar.OrderDate AS ⛓⚓search_date✖⚓,upar.STOCKITEMIDas ⛓⚓PolID✖⚓,UPPER(➕cls.ORDEREDOUTERS➖) as ⛓⚓outersname✖⚓,cln.ORDEREDOUTERS as ⛓⚓outersid✖⚓,upar.ORDEREDOUTERS as ⛓⚓parent_PolID✖⚓,UPPER(➕pls.ORDEREDOUTERS➖) as ⛓⚓parent_outersname✖⚓,pln.ORDEREDOUTERS as ⛓⚓parent_outersid ❌from⚓ unique_parent upar ❌left⚓ ❌join⚓ unique_purchase uprc ❌on⚓ uprc.STOCKITEMID ⚫=⚫ upar.STOCKITEMID ✖and⚓ uprc.OrderDate ⚫=⚫ upar.OrderDate ❌left⚓ ❌join⚓ unique_purchase uprcs ❌on⚓ pls.STOCKITEMID ⚫=⚫ upar.ORDEREDOUTERS ✖and⚓ uprcs.OrderDate ⚫=⚫ upar.OrderDate ❌left⚓ ❌join⚓ unique_item uit ❌on⚓ cln.STOCKITEMID ⚫=⚫ upar.STOCKITEMID ✖and⚓ uit.OrderDate ⚫=⚫ upar.OrderDate ❌left⚓ ❌join⚓ unique_item uitem ❌on⚓ uitem.STOCKITEMID ⚫=⚫ upar.ORDEREDOUTERS ✖and⚓ uitem.OrderDate ⚫=⚫ upar.OrderDate⛓⚓➖)❌,navigate_hierarchy as(➕❌ SELECT⚓ search_date✖⚓,PolID✖⚓,outersid✖⚓,cast(➕outersname as varchar➖) as ⛓⚓outersname✖⚓,parent_PolID✖⚓,parent_outersid✖⚓,cast(➕parent_outersname as varchar➖) as ⛓⚓parent_outersname✖⚓,1 as ⛓⚓ParentLevel✖⚓,concat(➕ cast(➕outersname as varchar➖)✖⚓,' -> '✖⚓,cast(➕parent_outersname as varchar➖)➖) as ⛓⚓outersnameline ❌from⚓ parent_child ❌UNION ALL⚓❌ SELECT⚓ c.search_date✖⚓,c.PolID✖⚓,c.outersid✖⚓,cast(➕c.outersname as varchar➖) as ⛓⚓outersname✖⚓,p.parent_PolID✖⚓,p.parent_outersid✖⚓,cast(➕p.parent_outersname as varchar➖) as ⛓⚓parent_outersname✖⚓,p.ParentLevel ⚫+⚫ 1✖⚓,cast(➕ CONCAT(➕ cast(➕c.outersname as varchar➖)✖⚓,' -> '✖⚓,cast(➕p.outersnameline as varchar➖)➖) AS varchar➖) as ⛓⚓outersnameline ❌from⚓ parent_child C ❌join⚓ navigate_hierarchy p ❌on⚓ p.PolID ⚫=⚫ c.parent_PolID ✖AND⚓ c.PolID ⚫<>⚫ c.parent_PolID ✖and⚓ p.ParentLevel ⚫<=⚫ 40 ✖AND⚓ p.search_date ⚫=⚫ c.search_date ❌where⚓ p.ParentLevel ⚫<=⚫ 40⛓⚓➖)❌,TEST_OUTPUT AS(➕❌ select⚓ DISTINCT ID✖⚓,search_date✖⚓,orderedouters✖⚓,PAYMENTMETHODID✖⚓,TRANSACTIONDATE✖⚓,PolID✖⚓,outersid✖⚓,outersname✖⚓,STOCKITEMID✖⚓,ParentLevel✖⚓,ParentLevel_Desc✖⚓,PolID as ⛓⚓parent_PolID✖⚓,outersid as ⛓⚓parent_outersid✖⚓,outersname as ⛓⚓parent_outersname✖⚓,outersname as ⛓⚓outersnameline ❌from⚓ direct_mapping ❌UNION⚓❌ select⚓ CONCAT(➕dm.orderedouters✖⚓,'-'✖⚓,nh.Parentlevel➖) as ⛓⚓ID✖⚓,dm.search_date✖⚓,dm.orderedouters✖⚓,dm.PAYMENTMETHODID✖⚓,dm.TRANSACTIONDATE✖⚓,nh.PolID✖⚓,nh.outersid✖⚓,nh.outersname✖⚓,dm.STOCKITEMID✖⚓,nh.ParentLevel✖⚓,❌CASE⚓➕ ❌WHEN⚓ nh.ParentLevel ⚫=⚫ 1 ❌THEN⚓ 'Immediate Parent of Salesperson Issuer' ❌ELSE⚓ concat(➕ 'Higher Level Parent ('✖⚓,nh.ParentLevel✖⚓,') Levels above the Salesperson Issuer'➖) ➖❌END⚓ as ⛓⚓ParentLevel_Desc✖⚓,parent_PolID✖⚓,parent_outersid✖⚓,parent_outersname✖⚓,outersnameline as ⛓⚓outersnameline ❌from⚓ navigate_hierarchy nh ❌inner⚓ ❌join⚓ direct_map dm ❌on⚓ dm.PolID ⚫=⚫ nh.PolID⛓⚓➖)❌SELECT⚓ *❌FROM⚓ TEST_OUTPUT ❌group⚓ by search_date"""

        expected = """WITH date_list AS(
    SELECT CAST('2021-05-24' AS date) AS 
          OrderDate 
     UNION
    SELECT CAST('2021-05-25' AS date) AS 
          OrderDate
          )
,unique_orderedouters AS(
    select PURCHASEORDERLINEID
          ,ORDEREDOUTERS
          ,dl.OrderDate 
      from PURCHASING_PURCHASEORDERLINES a 
      JOIN date_list dl 
        ON a.LASTRECEIPTDATE <= OrderDate
       AND( a.LASTEDITEDWHEN > OrderDate
            OR a.LASTEDITEDWHEN is NULL) 
     where a.PURCHASEORDERID = 27229
       and a.STOCKITEMID = 1
   QUALIFY ROW_NUMBER() OVER( PARTITION BY ORDEREDOUTERS 
         ORDER BY RECEIVEDOUTERS DESC) = 1
          )
,unique_purchase as(
    select STOCKITEMID
          ,ORDEREDOUTERS
          ,dl.OrderDate 
      from PURCHASING_PURCHASEORDERLINES a 
      JOIN date_list dl 
        ON a.LASTRECEIPTDATE <= OrderDate
       AND( a.LASTEDITEDWHEN > OrderDate
            OR a.LASTEDITEDWHEN is NULL) 
     where a.PURCHASEORDERID = 27033
       and a.STOCKITEMID = 1
   QUALIFY ROW_NUMBER() OVER( PARTITION BY ORDEREDOUTERS 
         ORDER BY RECEIVEDOUTERS DESC) = 1
          )
,unique_item as(
    select STOCKITEMID
          ,ORDEREDOUTERS
          ,dl.OrderDate 
      from PURCHASING_PURCHASEORDERLINES a 
      JOIN date_list dl 
        ON a.LASTRECEIPTDATE <= OrderDate
       AND( a.LASTEDITEDWHEN > OrderDate
            OR a.LASTEDITEDWHEN is NULL) 
     where a.PURCHASEORDERID = 114364
       and a.STOCKITEMID = 1
   QUALIFY ROW_NUMBER() OVER( PARTITION BY ORDEREDOUTERS 
         ORDER BY RECEIVEDOUTERS DESC) = 1
          )
,unique_parent as(
    select STOCKITEMID
          ,ORDEREDOUTERS
          ,dl.OrderDate 
      from PURCHASING_PURCHASEORDERLINES a 
      JOIN date_list dl 
        ON a.LASTRECEIPTDATE <= OrderDate
       AND( a.LASTEDITEDWHEN > OrderDate
            OR a.LASTEDITEDWHEN is NULL) 
     where a.PURCHASEORDERID = 34559
       and a.STOCKITEMID = 1
   QUALIFY ROW_NUMBER() OVER( PARTITION BY ORDEREDOUTERS 
         ORDER BY RECEIVEDOUTERS DESC) = 1
          )
,purchase_con AS(
    select DISTINCT CONCAT(pol.ORDEREDOUTERS
              ,'-0') as 
          ID
          ,dl.OrderDate as 
          search_date
          ,pol.ORDEREDOUTERS as 
          orderedouters
          ,sinv.ORDERID
          ,sct.PAYMENTMETHODID
          ,sct.TRANSACTIONDATE
          ,up.PURCHASEORDERLINEID as 
          PolID
          ,ui.ORDEREDOUTERS as 
          outersid
          ,UPPER(up.ORDEREDOUTERS) as 
          outersname
          ,sinvl.STOCKITEMID
          ,0 as 
          ParentLevel
          ,'Direct Issuer of the Voucher' as 
          ParentLevel_Desc 
      from PURCHASING_PURCHASEORDERLINES pol 
     inner 
      join SALES_ORDERS sord 
        on sord.ORDERID = pol.PURCHASEORDERID
       and pol.PURCHASEORDERID = 35
       and pol.STOCKITEMID = 1
       and sord.SALESPERSONPERSONID = 1
       and sord.CONTACTPERSONID = 1
       and sord.DELIVERYINSTRUCTIONS = 'SHR'
       AND pol.ORDEREDOUTERS IS NOT NULL 
       AND sord.CUSTOMERPURCHASEORDERNUMBER is not null 
     inner 
      join SALES_INVOICES sinv 
        on sinv.ORDERID = sord.ORDERID
     INNER 
      JOIN SALES_CUSTOMERS AS scus 
        ON scus.CUSTOMERID = sinv.CUSTOMERID
     INNER 
      JOIN SALES_CUSTOMERTRANSACTIONS AS sct 
        ON sct.CUSTOMERID = scus.CUSTOMERID
     INNER 
      JOIN SALES_INVOICELINES AS sinvl 
        ON sinvl.INVOICEID = sct.INVOICEID
     INNER 
      join unique_purchase up 
        on ui.STOCKITEMID = sinvl.STOCKITEMID
      LEFT 
      join unique_item ui 
        on ui.STOCKITEMID = sinvl.STOCKITEMID
     INNER 
      JOIN date_list dl 
        ON pol.LASTRECEIPTDATE <= dl.OrderDate
       AND( pol.LASTEDITEDWHEN > dl.OrderDate
            OR pol.LASTEDITEDWHEN is NULL) 
       AND sinv.INVOICEDATE <= dl.OrderDate
       AND( sinv.LASTEDITEDWHEN > dl.OrderDate
            OR sinv.LASTEDITEDWHEN is NULL) 
     where pol.STOCKITEMID = 35
       and pol.STOCKITEMID = 1
       AND pol.ORDEREDOUTERS IS NOT NULL 
       and sord.SALESPERSONPERSONID = 1
       and sord.CONTACTPERSONID = 1
       and sord.DELIVERYINSTRUCTIONS = 'SHR'
       AND sord.CUSTOMERPURCHASEORDERNUMBER is not null
          )
,rule AS(
    select distinct CONCAT(orderedouters.ORDEREDOUTERS
              ,'-0') as 
          ID
          ,orderedouters.OrderDate as 
          search_date
          ,orderedouters.ORDEREDOUTERS as 
          orderedouters
          ,sct.PAYMENTMETHODID
          ,sct.TRANSACTIONDATE
          ,up.PURCHASEORDERLINEID as 
          PolID
          ,ui.ORDEREDOUTERS as 
          outersid
          ,UPPER(up.ORDEREDOUTERS) as 
          outersname
          ,sinvl.STOCKITEMID
          ,0 as 
          ParentLevel
          ,'Direct Issuer of Salesperson' as 
          ParentLevel_Desc 
      from unique_orderedouters orderedouters 
     inner 
      join SALES_CUSTOMERTRANSACTIONS sct 
        on orderedouters.PURCHASEORDERLINEID = sct.PURCHASEORDERLINEID
     inner 
      join SALES_INVOICELINES sinvl 
        on sinvl.INVOICEID = sct.INVOICEID
     inner 
      join unique_purchase up 
        on up.PURCHASEORDERLINEID = sinvl.PURCHASEORDERLINEID
      LEFT 
      join unique_item up 
        on ui.PURCHASEORDERLINEID = sinvl.PURCHASEORDERLINEID
       and ui.OrderDate = orderedouters.OrderDate
     where sct.ISFINALIZED in('TRUE')
          )
,direct_map AS(
    select ID
          ,search_date
          ,orderedouters
          ,PAYMENTMETHODID
          ,TRANSACTIONDATE
          ,PolID
          ,outersid
          ,outersname
          ,STOCKITEMID
          ,ParentLevel
          ,ParentLevel_Desc 
      from purchase_con 
     UNION
    select ID
          ,search_date
          ,orderedouters
          ,PAYMENTMETHODID
          ,TRANSACTIONDATE
          ,PolID
          ,outersid
          ,outersname
          ,STOCKITEMID
          ,ParentLevel
          ,ParentLevel_Desc 
      from rule 
     where ID not in( select distinct ID 
                         from purchase_con)
          )
,parent_child AS(
    select Distinct upar.OrderDate AS 
          search_date
          ,upar.STOCKITEMIDas 
          PolID
          ,UPPER(cls.ORDEREDOUTERS) as 
          outersname
          ,cln.ORDEREDOUTERS as 
          outersid
          ,upar.ORDEREDOUTERS as 
          parent_PolID
          ,UPPER(pls.ORDEREDOUTERS) as 
          parent_outersname
          ,pln.ORDEREDOUTERS as 
          parent_outersid 
      from unique_parent upar 
      left 
      join unique_purchase uprc 
        on uprc.STOCKITEMID = upar.STOCKITEMID
       and uprc.OrderDate = upar.OrderDate
      left 
      join unique_purchase uprcs 
        on pls.STOCKITEMID = upar.ORDEREDOUTERS
       and uprcs.OrderDate = upar.OrderDate
      left 
      join unique_item uit 
        on cln.STOCKITEMID = upar.STOCKITEMID
       and uit.OrderDate = upar.OrderDate
      left 
      join unique_item uitem 
        on uitem.STOCKITEMID = upar.ORDEREDOUTERS
       and uitem.OrderDate = upar.OrderDate
          )
,navigate_hierarchy as(
    SELECT search_date
          ,PolID
          ,outersid
          ,cast(outersname as varchar) as 
          outersname
          ,parent_PolID
          ,parent_outersid
          ,cast(parent_outersname as varchar) as 
          parent_outersname
          ,1 as 
          ParentLevel
          ,concat( cast(outersname as varchar)
                             ,' -> '
                             ,cast(parent_outersname as varchar)) as 
          outersnameline 
      from parent_child 
   UNION ALL
    SELECT c.search_date
          ,c.PolID
          ,c.outersid
          ,cast(c.outersname as varchar) as 
          outersname
          ,p.parent_PolID
          ,p.parent_outersid
          ,cast(p.parent_outersname as varchar) as 
          parent_outersname
          ,p.ParentLevel + 1
          ,cast( CONCAT( cast(c.outersname as varchar)
                  ,' -> '
                  ,cast(p.outersnameline as varchar)) AS varchar) as 
          outersnameline 
      from parent_child C 
      join navigate_hierarchy p 
        on p.PolID = c.parent_PolID
       AND c.PolID <> c.parent_PolID
       and p.ParentLevel <= 40
       AND p.search_date = c.search_date
     where p.ParentLevel <= 40
          )
,TEST_OUTPUT AS(
    select DISTINCT ID
          ,search_date
          ,orderedouters
          ,PAYMENTMETHODID
          ,TRANSACTIONDATE
          ,PolID
          ,outersid
          ,outersname
          ,STOCKITEMID
          ,ParentLevel
          ,ParentLevel_Desc
          ,PolID as 
          parent_PolID
          ,outersid as 
          parent_outersid
          ,outersname as 
          parent_outersname
          ,outersname as 
          outersnameline 
      from direct_mapping 
     UNION
    select CONCAT(dm.orderedouters
                             ,'-'
                             ,nh.Parentlevel) as 
          ID
          ,dm.search_date
          ,dm.orderedouters
          ,dm.PAYMENTMETHODID
          ,dm.TRANSACTIONDATE
          ,nh.PolID
          ,nh.outersid
          ,nh.outersname
          ,dm.STOCKITEMID
          ,nh.ParentLevel
          ,
      CASE 
                         WHEN nh.ParentLevel = 1
                         THEN 'Immediate Parent of Salesperson Issuer' 
                         ELSE concat( 'Higher Level Parent ('
                  ,nh.ParentLevel
                  ,') Levels above the Salesperson Issuer') 
       END as 
          ParentLevel_Desc
          ,parent_PolID
          ,parent_outersid
          ,parent_outersname
          ,outersnameline as 
          outersnameline 
      from navigate_hierarchy nh 
     inner 
      join direct_map dm 
        on dm.PolID = nh.PolID
          )
SELECT *
  FROM TEST_OUTPUT 
 group by search_date"""

        self.assertEqual(expected, _process_data(marked_sql, "comfortable"))

    def test_sample_complex_compact(self):
        marked_sql = """WITH← date_list AS(➕❌ SELECT⚓ CAST(➕'2021-05-24' AS date➖) AS ⛓⚓OrderDate ❌UNION⚓❌ SELECT⚓ CAST(➕'2021-05-25' AS date➖) AS ⛓⚓OrderDate⛓⚓➖)❌,unique_orderedouters AS(➕❌ select⚓ PURCHASEORDERLINEID✖⚓,ORDEREDOUTERS✖⚓,dl.OrderDate ❌from⚓ PURCHASING_PURCHASEORDERLINES a ❌JOIN⚓ date_list dl ❌ON⚓ a.LASTRECEIPTDATE ⚫<=⚫ OrderDate ✖AND⚓(➕ a.LASTEDITEDWHEN ⚫>⚫ OrderDate ✖OR⚓ a.LASTEDITEDWHEN is NULL➖) ❌where⚓ a.PURCHASEORDERID ⚫=⚫ 27229 ✖and⚓ a.STOCKITEMID ⚫=⚫ 1 ❌QUALIFY⚓ ROW_NUMBER(➕➖) OVER(➕ PARTITION⧆ BY ORDEREDOUTERS ❌ORDER⚓⧆ BY RECEIVEDOUTERS DESC➖) ⚫=⚫ 1⛓⚓➖)❌,unique_purchase as(➕❌ select⚓ STOCKITEMID✖⚓,ORDEREDOUTERS✖⚓,dl.OrderDate ❌from⚓ PURCHASING_PURCHASEORDERLINES a ❌JOIN⚓ date_list dl ❌ON⚓ a.LASTRECEIPTDATE ⚫<=⚫ OrderDate ✖AND⚓(➕ a.LASTEDITEDWHEN ⚫>⚫ OrderDate ✖OR⚓ a.LASTEDITEDWHEN is NULL➖) ❌where⚓ a.PURCHASEORDERID ⚫=⚫ 27033 ✖and⚓ a.STOCKITEMID ⚫=⚫ 1 ❌QUALIFY⚓ ROW_NUMBER(➕➖) OVER(➕ PARTITION⧆ BY ORDEREDOUTERS ❌ORDER⚓⧆ BY RECEIVEDOUTERS DESC➖) ⚫=⚫ 1⛓⚓➖)❌,unique_item as(➕❌ select⚓ STOCKITEMID✖⚓,ORDEREDOUTERS✖⚓,dl.OrderDate ❌from⚓ PURCHASING_PURCHASEORDERLINES a ❌JOIN⚓ date_list dl ❌ON⚓ a.LASTRECEIPTDATE ⚫<=⚫ OrderDate ✖AND⚓(➕ a.LASTEDITEDWHEN ⚫>⚫ OrderDate ✖OR⚓ a.LASTEDITEDWHEN is NULL➖) ❌where⚓ a.PURCHASEORDERID ⚫=⚫ 114364 ✖and⚓ a.STOCKITEMID ⚫=⚫ 1 ❌QUALIFY⚓ ROW_NUMBER(➕➖) OVER(➕ PARTITION⧆ BY ORDEREDOUTERS ❌ORDER⚓⧆ BY RECEIVEDOUTERS DESC➖) ⚫=⚫ 1⛓⚓➖)❌,unique_parent as(➕❌ select⚓ STOCKITEMID✖⚓,ORDEREDOUTERS✖⚓,dl.OrderDate ❌from⚓ PURCHASING_PURCHASEORDERLINES a ❌JOIN⚓ date_list dl ❌ON⚓ a.LASTRECEIPTDATE ⚫<=⚫ OrderDate ✖AND⚓(➕ a.LASTEDITEDWHEN ⚫>⚫ OrderDate ✖OR⚓ a.LASTEDITEDWHEN is NULL➖) ❌where⚓ a.PURCHASEORDERID ⚫=⚫ 34559 ✖and⚓ a.STOCKITEMID ⚫=⚫ 1 ❌QUALIFY⚓ ROW_NUMBER(➕➖) OVER(➕ PARTITION⧆ BY ORDEREDOUTERS ❌ORDER⚓⧆ BY RECEIVEDOUTERS DESC➖) ⚫=⚫ 1⛓⚓➖)❌,purchase_con AS(➕❌ select⚓ DISTINCT CONCAT(➕pol.ORDEREDOUTERS✖⚓,'-0'➖) as ⛓⚓ID✖⚓,dl.OrderDate as ⛓⚓search_date✖⚓,pol.ORDEREDOUTERS as ⛓⚓orderedouters✖⚓,sinv.ORDERID✖⚓,sct.PAYMENTMETHODID✖⚓,sct.TRANSACTIONDATE✖⚓,up.PURCHASEORDERLINEID as ⛓⚓PolID✖⚓,ui.ORDEREDOUTERS as ⛓⚓outersid✖⚓,UPPER(➕up.ORDEREDOUTERS➖) as ⛓⚓outersname✖⚓,sinvl.STOCKITEMID✖⚓,0 as ⛓⚓ParentLevel✖⚓,'Direct Issuer of the Voucher' as ⛓⚓ParentLevel_Desc ❌from⚓ PURCHASING_PURCHASEORDERLINES pol ❌inner⚓ ❌join⚓ SALES_ORDERS sord ❌on⚓ sord.ORDERID ⚫=⚫ pol.PURCHASEORDERID ✖and⚓ pol.PURCHASEORDERID ⚫=⚫ 35 ✖and⚓ pol.STOCKITEMID ⚫=⚫ 1 ✖and⚓ sord.SALESPERSONPERSONID ⚫=⚫ 1 ✖and⚓ sord.CONTACTPERSONID⚫=⚫ 1 ✖and⚓ sord.DELIVERYINSTRUCTIONS ⚫=⚫ 'SHR' ✖AND⚓ pol.ORDEREDOUTERS IS NOT NULL ✖AND⚓ sord.CUSTOMERPURCHASEORDERNUMBER is not null ❌inner⚓ ❌join⚓ SALES_INVOICES sinv ❌on⚓ sinv.ORDERID ⚫=⚫ sord.ORDERID ❌INNER⚓ ❌JOIN⚓ SALES_CUSTOMERS AS scus ❌ON⚓ scus.CUSTOMERID ⚫=⚫ sinv.CUSTOMERID ❌INNER⚓ ❌JOIN⚓ SALES_CUSTOMERTRANSACTIONS AS sct ❌ON⚓ sct.CUSTOMERID ⚫=⚫ scus.CUSTOMERID ❌INNER⚓ ❌JOIN⚓ SALES_INVOICELINES AS sinvl ❌ON⚓ sinvl.INVOICEID ⚫=⚫ sct.INVOICEID ❌INNER⚓ ❌join⚓ unique_purchase up ❌on⚓ ui.STOCKITEMID ⚫=⚫ sinvl.STOCKITEMID ❌LEFT⚓ ❌join⚓ unique_item ui ❌on⚓ ui.STOCKITEMID ⚫=⚫ sinvl.STOCKITEMID ❌INNER⚓ ❌JOIN⚓ date_list dl ❌ON⚓ pol.LASTRECEIPTDATE⚫<=⚫ dl.OrderDate ✖AND⚓(➕ pol.LASTEDITEDWHEN ⚫>⚫ dl.OrderDate ✖OR⚓ pol.LASTEDITEDWHEN is NULL➖) ✖AND⚓ sinv.INVOICEDATE ⚫<=⚫ dl.OrderDate ✖AND⚓(➕ sinv.LASTEDITEDWHEN ⚫>⚫ dl.OrderDate ✖OR⚓ sinv.LASTEDITEDWHEN is NULL➖) ❌where⚓ pol.STOCKITEMID ⚫=⚫ 35 ✖and⚓ pol.STOCKITEMID ⚫=⚫ 1 ✖AND⚓ pol.ORDEREDOUTERS IS NOT NULL ✖and⚓ sord.SALESPERSONPERSONID ⚫=⚫ 1 ✖and⚓ sord.CONTACTPERSONID⚫=⚫ 1 ✖and⚓ sord.DELIVERYINSTRUCTIONS ⚫=⚫ 'SHR' ✖AND⚓ sord.CUSTOMERPURCHASEORDERNUMBER is not null⛓⚓➖)❌,rule AS(➕❌ select⚓ distinct CONCAT(➕orderedouters.ORDEREDOUTERS✖⚓,'-0'➖) as ⛓⚓ID✖⚓,orderedouters.OrderDate as ⛓⚓search_date✖⚓,orderedouters.ORDEREDOUTERS as ⛓⚓orderedouters✖⚓,sct.PAYMENTMETHODID✖⚓,sct.TRANSACTIONDATE✖⚓,up.PURCHASEORDERLINEID as ⛓⚓PolID✖⚓,ui.ORDEREDOUTERS as ⛓⚓outersid✖⚓,UPPER(➕up.ORDEREDOUTERS➖) as ⛓⚓outersname✖⚓,sinvl.STOCKITEMID✖⚓,0 as ⛓⚓ParentLevel✖⚓,'Direct Issuer of Salesperson' as ⛓⚓ParentLevel_Desc ❌from⚓ unique_orderedouters orderedouters ❌inner⚓ ❌join⚓ SALES_CUSTOMERTRANSACTIONS sct ❌on⚓ orderedouters.PURCHASEORDERLINEID ⚫=⚫ sct.PURCHASEORDERLINEID ❌inner⚓ ❌join⚓ SALES_INVOICELINES sinvl ❌on⚓ sinvl.INVOICEID ⚫=⚫ sct.INVOICEID ❌inner⚓ ❌join⚓ unique_purchase up ❌on⚓ up.PURCHASEORDERLINEID ⚫=⚫ sinvl.PURCHASEORDERLINEID ❌LEFT⚓ ❌join⚓ unique_item up ❌on⚓ ui.PURCHASEORDERLINEID ⚫=⚫ sinvl.PURCHASEORDERLINEID ✖and⚓ ui.OrderDate ⚫=⚫ orderedouters.OrderDate ❌where⚓ sct.ISFINALIZED in(➕'TRUE'➖)⛓⚓➖)❌,direct_map AS(➕❌ select⚓ ID✖⚓,search_date✖⚓,orderedouters✖⚓,PAYMENTMETHODID✖⚓,TRANSACTIONDATE✖⚓,PolID✖⚓,outersid✖⚓,outersname✖⚓,STOCKITEMID✖⚓,ParentLevel✖⚓,ParentLevel_Desc ❌from⚓ purchase_con ❌UNION⚓❌ select⚓ ID✖⚓,search_date✖⚓,orderedouters✖⚓,PAYMENTMETHODID✖⚓,TRANSACTIONDATE✖⚓,PolID✖⚓,outersid✖⚓,outersname✖⚓,STOCKITEMID✖⚓,ParentLevel✖⚓,ParentLevel_Desc ❌from⚓ rule ❌where⚓ ID not in(➕ select⚓ distinct ID ❌from⚓ purchase_con➖)⛓⚓➖)❌,parent_child AS(➕❌ select⚓ Distinct upar.OrderDate AS ⛓⚓search_date✖⚓,upar.STOCKITEMIDas ⛓⚓PolID✖⚓,UPPER(➕cls.ORDEREDOUTERS➖) as ⛓⚓outersname✖⚓,cln.ORDEREDOUTERS as ⛓⚓outersid✖⚓,upar.ORDEREDOUTERS as ⛓⚓parent_PolID✖⚓,UPPER(➕pls.ORDEREDOUTERS➖) as ⛓⚓parent_outersname✖⚓,pln.ORDEREDOUTERS as ⛓⚓parent_outersid ❌from⚓ unique_parent upar ❌left⚓ ❌join⚓ unique_purchase uprc ❌on⚓ uprc.STOCKITEMID ⚫=⚫ upar.STOCKITEMID ✖and⚓ uprc.OrderDate ⚫=⚫ upar.OrderDate ❌left⚓ ❌join⚓ unique_purchase uprcs ❌on⚓ pls.STOCKITEMID ⚫=⚫ upar.ORDEREDOUTERS ✖and⚓ uprcs.OrderDate ⚫=⚫ upar.OrderDate ❌left⚓ ❌join⚓ unique_item uit ❌on⚓ cln.STOCKITEMID ⚫=⚫ upar.STOCKITEMID ✖and⚓ uit.OrderDate ⚫=⚫ upar.OrderDate ❌left⚓ ❌join⚓ unique_item uitem ❌on⚓ uitem.STOCKITEMID ⚫=⚫ upar.ORDEREDOUTERS ✖and⚓ uitem.OrderDate ⚫=⚫ upar.OrderDate⛓⚓➖)❌,navigate_hierarchy as(➕❌ SELECT⚓ search_date✖⚓,PolID✖⚓,outersid✖⚓,cast(➕outersname as varchar➖) as ⛓⚓outersname✖⚓,parent_PolID✖⚓,parent_outersid✖⚓,cast(➕parent_outersname as varchar➖) as ⛓⚓parent_outersname✖⚓,1 as ⛓⚓ParentLevel✖⚓,concat(➕ cast(➕outersname as varchar➖)✖⚓,' -> '✖⚓,cast(➕parent_outersname as varchar➖)➖) as ⛓⚓outersnameline ❌from⚓ parent_child ❌UNION ALL⚓❌ SELECT⚓ c.search_date✖⚓,c.PolID✖⚓,c.outersid✖⚓,cast(➕c.outersname as varchar➖) as ⛓⚓outersname✖⚓,p.parent_PolID✖⚓,p.parent_outersid✖⚓,cast(➕p.parent_outersname as varchar➖) as ⛓⚓parent_outersname✖⚓,p.ParentLevel ⚫+⚫ 1✖⚓,cast(➕ CONCAT(➕ cast(➕c.outersname as varchar➖)✖⚓,' -> '✖⚓,cast(➕p.outersnameline as varchar➖)➖) AS varchar➖) as ⛓⚓outersnameline ❌from⚓ parent_child C ❌join⚓ navigate_hierarchy p ❌on⚓ p.PolID ⚫=⚫ c.parent_PolID ✖AND⚓ c.PolID ⚫<>⚫ c.parent_PolID ✖and⚓ p.ParentLevel ⚫<=⚫ 40 ✖AND⚓ p.search_date ⚫=⚫ c.search_date ❌where⚓ p.ParentLevel ⚫<=⚫ 40⛓⚓➖)❌,TEST_OUTPUT AS(➕❌ select⚓ DISTINCT ID✖⚓,search_date✖⚓,orderedouters✖⚓,PAYMENTMETHODID✖⚓,TRANSACTIONDATE✖⚓,PolID✖⚓,outersid✖⚓,outersname✖⚓,STOCKITEMID✖⚓,ParentLevel✖⚓,ParentLevel_Desc✖⚓,PolID as ⛓⚓parent_PolID✖⚓,outersid as ⛓⚓parent_outersid✖⚓,outersname as ⛓⚓parent_outersname✖⚓,outersname as ⛓⚓outersnameline ❌from⚓ direct_mapping ❌UNION⚓❌ select⚓ CONCAT(➕dm.orderedouters✖⚓,'-'✖⚓,nh.Parentlevel➖) as ⛓⚓ID✖⚓,dm.search_date✖⚓,dm.orderedouters✖⚓,dm.PAYMENTMETHODID✖⚓,dm.TRANSACTIONDATE✖⚓,nh.PolID✖⚓,nh.outersid✖⚓,nh.outersname✖⚓,dm.STOCKITEMID✖⚓,nh.ParentLevel✖⚓,❌CASE⚓➕ ❌WHEN⚓ nh.ParentLevel ⚫=⚫ 1 ❌THEN⚓ 'Immediate Parent of Salesperson Issuer' ❌ELSE⚓ concat(➕ 'Higher Level Parent ('✖⚓,nh.ParentLevel✖⚓,') Levels above the Salesperson Issuer'➖) ➖❌END⚓ as ⛓⚓ParentLevel_Desc✖⚓,parent_PolID✖⚓,parent_outersid✖⚓,parent_outersname✖⚓,outersnameline as ⛓⚓outersnameline ❌from⚓ navigate_hierarchy nh ❌inner⚓ ❌join⚓ direct_map dm ❌on⚓ dm.PolID ⚫=⚫ nh.PolID⛓⚓➖)❌SELECT⚓ *❌FROM⚓ TEST_OUTPUT ❌group⚓ by search_date"""

        expected = """WITH date_list AS(
    SELECT CAST('2021-05-24' AS date) AS OrderDate 
     UNION
    SELECT CAST('2021-05-25' AS date) AS OrderDate)
,unique_orderedouters AS(
    select PURCHASEORDERLINEID
          ,ORDEREDOUTERS
          ,dl.OrderDate 
      from PURCHASING_PURCHASEORDERLINES a 
      JOIN date_list dl 
        ON a.LASTRECEIPTDATE<=OrderDate
       AND( a.LASTEDITEDWHEN>OrderDate
            OR a.LASTEDITEDWHEN is NULL) 
     where a.PURCHASEORDERID=27229
       and a.STOCKITEMID=1
   QUALIFY ROW_NUMBER() OVER( PARTITION BY ORDEREDOUTERS 
         ORDER BY RECEIVEDOUTERS DESC)=1)
,unique_purchase as(
    select STOCKITEMID
          ,ORDEREDOUTERS
          ,dl.OrderDate 
      from PURCHASING_PURCHASEORDERLINES a 
      JOIN date_list dl 
        ON a.LASTRECEIPTDATE<=OrderDate
       AND( a.LASTEDITEDWHEN>OrderDate
            OR a.LASTEDITEDWHEN is NULL) 
     where a.PURCHASEORDERID=27033
       and a.STOCKITEMID=1
   QUALIFY ROW_NUMBER() OVER( PARTITION BY ORDEREDOUTERS 
         ORDER BY RECEIVEDOUTERS DESC)=1)
,unique_item as(
    select STOCKITEMID
          ,ORDEREDOUTERS
          ,dl.OrderDate 
      from PURCHASING_PURCHASEORDERLINES a 
      JOIN date_list dl 
        ON a.LASTRECEIPTDATE<=OrderDate
       AND( a.LASTEDITEDWHEN>OrderDate
            OR a.LASTEDITEDWHEN is NULL) 
     where a.PURCHASEORDERID=114364
       and a.STOCKITEMID=1
   QUALIFY ROW_NUMBER() OVER( PARTITION BY ORDEREDOUTERS 
         ORDER BY RECEIVEDOUTERS DESC)=1)
,unique_parent as(
    select STOCKITEMID
          ,ORDEREDOUTERS
          ,dl.OrderDate 
      from PURCHASING_PURCHASEORDERLINES a 
      JOIN date_list dl 
        ON a.LASTRECEIPTDATE<=OrderDate
       AND( a.LASTEDITEDWHEN>OrderDate
            OR a.LASTEDITEDWHEN is NULL) 
     where a.PURCHASEORDERID=34559
       and a.STOCKITEMID=1
   QUALIFY ROW_NUMBER() OVER( PARTITION BY ORDEREDOUTERS 
         ORDER BY RECEIVEDOUTERS DESC)=1)
,purchase_con AS(
    select DISTINCT CONCAT(pol.ORDEREDOUTERS
              ,'-0') as ID
          ,dl.OrderDate as search_date
          ,pol.ORDEREDOUTERS as orderedouters
          ,sinv.ORDERID
          ,sct.PAYMENTMETHODID
          ,sct.TRANSACTIONDATE
          ,up.PURCHASEORDERLINEID as PolID
          ,ui.ORDEREDOUTERS as outersid
          ,UPPER(up.ORDEREDOUTERS) as outersname
          ,sinvl.STOCKITEMID
          ,0 as ParentLevel
          ,'Direct Issuer of the Voucher' as ParentLevel_Desc 
      from PURCHASING_PURCHASEORDERLINES pol 
     inner 
      join SALES_ORDERS sord 
        on sord.ORDERID=pol.PURCHASEORDERID
       and pol.PURCHASEORDERID=35
       and pol.STOCKITEMID=1
       and sord.SALESPERSONPERSONID=1
       and sord.CONTACTPERSONID=1
       and sord.DELIVERYINSTRUCTIONS='SHR'
       AND pol.ORDEREDOUTERS IS NOT NULL 
       AND sord.CUSTOMERPURCHASEORDERNUMBER is not null 
     inner 
      join SALES_INVOICES sinv 
        on sinv.ORDERID=sord.ORDERID
     INNER 
      JOIN SALES_CUSTOMERS AS scus 
        ON scus.CUSTOMERID=sinv.CUSTOMERID
     INNER 
      JOIN SALES_CUSTOMERTRANSACTIONS AS sct 
        ON sct.CUSTOMERID=scus.CUSTOMERID
     INNER 
      JOIN SALES_INVOICELINES AS sinvl 
        ON sinvl.INVOICEID=sct.INVOICEID
     INNER 
      join unique_purchase up 
        on ui.STOCKITEMID=sinvl.STOCKITEMID
      LEFT 
      join unique_item ui 
        on ui.STOCKITEMID=sinvl.STOCKITEMID
     INNER 
      JOIN date_list dl 
        ON pol.LASTRECEIPTDATE<=dl.OrderDate
       AND( pol.LASTEDITEDWHEN>dl.OrderDate
            OR pol.LASTEDITEDWHEN is NULL) 
       AND sinv.INVOICEDATE<=dl.OrderDate
       AND( sinv.LASTEDITEDWHEN>dl.OrderDate
            OR sinv.LASTEDITEDWHEN is NULL) 
     where pol.STOCKITEMID=35
       and pol.STOCKITEMID=1
       AND pol.ORDEREDOUTERS IS NOT NULL 
       and sord.SALESPERSONPERSONID=1
       and sord.CONTACTPERSONID=1
       and sord.DELIVERYINSTRUCTIONS='SHR'
       AND sord.CUSTOMERPURCHASEORDERNUMBER is not null)
,rule AS(
    select distinct CONCAT(orderedouters.ORDEREDOUTERS
              ,'-0') as ID
          ,orderedouters.OrderDate as search_date
          ,orderedouters.ORDEREDOUTERS as orderedouters
          ,sct.PAYMENTMETHODID
          ,sct.TRANSACTIONDATE
          ,up.PURCHASEORDERLINEID as PolID
          ,ui.ORDEREDOUTERS as outersid
          ,UPPER(up.ORDEREDOUTERS) as outersname
          ,sinvl.STOCKITEMID
          ,0 as ParentLevel
          ,'Direct Issuer of Salesperson' as ParentLevel_Desc 
      from unique_orderedouters orderedouters 
     inner 
      join SALES_CUSTOMERTRANSACTIONS sct 
        on orderedouters.PURCHASEORDERLINEID=sct.PURCHASEORDERLINEID
     inner 
      join SALES_INVOICELINES sinvl 
        on sinvl.INVOICEID=sct.INVOICEID
     inner 
      join unique_purchase up 
        on up.PURCHASEORDERLINEID=sinvl.PURCHASEORDERLINEID
      LEFT 
      join unique_item up 
        on ui.PURCHASEORDERLINEID=sinvl.PURCHASEORDERLINEID
       and ui.OrderDate=orderedouters.OrderDate
     where sct.ISFINALIZED in('TRUE'))
,direct_map AS(
    select ID
          ,search_date
          ,orderedouters
          ,PAYMENTMETHODID
          ,TRANSACTIONDATE
          ,PolID
          ,outersid
          ,outersname
          ,STOCKITEMID
          ,ParentLevel
          ,ParentLevel_Desc 
      from purchase_con 
     UNION
    select ID
          ,search_date
          ,orderedouters
          ,PAYMENTMETHODID
          ,TRANSACTIONDATE
          ,PolID
          ,outersid
          ,outersname
          ,STOCKITEMID
          ,ParentLevel
          ,ParentLevel_Desc 
      from rule 
     where ID not in( select distinct ID 
                         from purchase_con))
,parent_child AS(
    select Distinct upar.OrderDate AS search_date
          ,upar.STOCKITEMIDas PolID
          ,UPPER(cls.ORDEREDOUTERS) as outersname
          ,cln.ORDEREDOUTERS as outersid
          ,upar.ORDEREDOUTERS as parent_PolID
          ,UPPER(pls.ORDEREDOUTERS) as parent_outersname
          ,pln.ORDEREDOUTERS as parent_outersid 
      from unique_parent upar 
      left 
      join unique_purchase uprc 
        on uprc.STOCKITEMID=upar.STOCKITEMID
       and uprc.OrderDate=upar.OrderDate
      left 
      join unique_purchase uprcs 
        on pls.STOCKITEMID=upar.ORDEREDOUTERS
       and uprcs.OrderDate=upar.OrderDate
      left 
      join unique_item uit 
        on cln.STOCKITEMID=upar.STOCKITEMID
       and uit.OrderDate=upar.OrderDate
      left 
      join unique_item uitem 
        on uitem.STOCKITEMID=upar.ORDEREDOUTERS
       and uitem.OrderDate=upar.OrderDate)
,navigate_hierarchy as(
    SELECT search_date
          ,PolID
          ,outersid
          ,cast(outersname as varchar) as outersname
          ,parent_PolID
          ,parent_outersid
          ,cast(parent_outersname as varchar) as parent_outersname
          ,1 as ParentLevel
          ,concat( cast(outersname as varchar)
                             ,' -> '
                             ,cast(parent_outersname as varchar)) as outersnameline 
      from parent_child 
   UNION ALL
    SELECT c.search_date
          ,c.PolID
          ,c.outersid
          ,cast(c.outersname as varchar) as outersname
          ,p.parent_PolID
          ,p.parent_outersid
          ,cast(p.parent_outersname as varchar) as parent_outersname
          ,p.ParentLevel+1
          ,cast( CONCAT( cast(c.outersname as varchar)
                  ,' -> '
                  ,cast(p.outersnameline as varchar)) AS varchar) as outersnameline 
      from parent_child C 
      join navigate_hierarchy p 
        on p.PolID=c.parent_PolID
       AND c.PolID<>c.parent_PolID
       and p.ParentLevel<=40
       AND p.search_date=c.search_date
     where p.ParentLevel<=40)
,TEST_OUTPUT AS(
    select DISTINCT ID
          ,search_date
          ,orderedouters
          ,PAYMENTMETHODID
          ,TRANSACTIONDATE
          ,PolID
          ,outersid
          ,outersname
          ,STOCKITEMID
          ,ParentLevel
          ,ParentLevel_Desc
          ,PolID as parent_PolID
          ,outersid as parent_outersid
          ,outersname as parent_outersname
          ,outersname as outersnameline 
      from direct_mapping 
     UNION
    select CONCAT(dm.orderedouters
                             ,'-'
                             ,nh.Parentlevel) as ID
          ,dm.search_date
          ,dm.orderedouters
          ,dm.PAYMENTMETHODID
          ,dm.TRANSACTIONDATE
          ,nh.PolID
          ,nh.outersid
          ,nh.outersname
          ,dm.STOCKITEMID
          ,nh.ParentLevel
          ,
      CASE 
                         WHEN nh.ParentLevel=1
                         THEN 'Immediate Parent of Salesperson Issuer' 
                         ELSE concat( 'Higher Level Parent ('
                  ,nh.ParentLevel
                  ,') Levels above the Salesperson Issuer') 
       END as ParentLevel_Desc
          ,parent_PolID
          ,parent_outersid
          ,parent_outersname
          ,outersnameline as outersnameline 
      from navigate_hierarchy nh 
     inner 
      join direct_map dm 
        on dm.PolID=nh.PolID)
SELECT *
  FROM TEST_OUTPUT 
 group by search_date"""

        self.assertEqual(expected, _process_data(marked_sql, "compact"))
