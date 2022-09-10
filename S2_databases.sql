
-- Question 1
select dim_customer.id, sum(dim_car.price) as total_spendings 
from dim_customer 
	left join transaction txn
		on dim_customer.id = txn.customerid
	left join dim_car
		on txn.carid = dim_car.id
	group by dim_customer.id; 



-- Question 2
select manufacturer , txn_cnt from ( 
	select * , dense_rank over (partition by manufacturer , order by txn_cnt desc) as rnk  
	from ( 
		select dim_car.manufacturer, count(txn.id) as txn_cnt 
		from ( 
			select * 
			from transaction where 
			transaction_date between '2022-09-01' and '2022-09-30'
		)txn 
		left join  dim_car 
			on txn.carid = dim_car.id
		group by dim_car.manfacturer
	)base 
)final 
where rnk <=3; 