# 2022-XML

## 주문검색기능
– 검색 요청
고객 : customers 테이블에 있는 고객(name)을 오름차순으로 나열하고, 사용자가 특정 고객을 선택할 수 있음.
국가 : customers 테이블에 있는 국가(country)를 오름차순으로 나열하고, 사용자가 특정 국가를 선택할 수 있음.
도시 : customers 테이블에 있는 도시(city)를 오름차순으로 나열하고, 사용자가 특정 도시를 선택할 수 있음.
고객, 국가, 도시에 각각 “ALL“이라는 값이 맨 앞에 있어야 함.
초기에는 고객의 “ALL”이 선택된 것으로 가정하고, 검색 결과를 출력함.

– “검색된 주문의 개수“에는 검색된 주문의 개수를 출력함.

– 검색된 주문은 다음과 같은 속성으로 구성하여 이 순서대로 출력함.
orderNo, orderDate, requiredDate, shippedDate, status, customer, comments

☞ customer는 customers 테이블의 name을 출력함.

– 검색된 주문 리스트는 orderNo의 오름차순으로 정렬함.

– 주문 리스트에서 특정 주문을 선택하면, “주문 상세 내역“ 화면이 독립적으로 나타남.

## 주문 상세 내역 출력 기능

- 주문에 포함된 상품 정보는 다음과 같이 구성하여 출력함.
orderLineNo, productCode, productName, quantity, priceEach, 상품주문액
☞ productName은 products 테이블의 name을 출력함. ☞ 상품주문액은 quantity × priceEach로 계산함.

– 주문에 포함된 상품 리스트는 orderLineNo의 오름차순으로 정렬함.

– “상품개수“ 에는 주문에 포함된 상품의 개수를 출력함.  상품의 주문 개수(quantity)의 합이 아님.

– “주문액“에는 주문에 포함된 상품의 “상품주문액“의 합을 출력함.
