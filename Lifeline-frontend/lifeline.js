
    const API_URL = 'http://127.0.0.1';

    const totalProfitEl = document.getElementById('totalProfit');
    const moneyDebtsEl = document.getElementById('moneyDebts');
    const cashFlowEl = document.getElementById('cashFlow');

    function loadDashboardData() {
     
      fetch(`${API_URL}/summary`)
        .then(res => res.json())
        .then(data => {
          totalProfitEl.innerText = `Ksh ${parseFloat(data.total_profit_earned || 0).toFixed(2)}`;
          moneyDebtsEl.innerText = `Ksh ${parseFloat(data.money_tied_in_debts || 0).toFixed(2)}`;
          cashFlowEl.innerText = `Ksh ${parseFloat(data.actual_take_home_cash || 0).toFixed(2)}`;
        })
        .catch(err => console.error("Error fetching financial totals summary:", err));
    }

    document.addEventListener('DOMContentLoaded', loadDashboardData);




   
    const productSelectEl = document.getElementById('productSelect');
    const quantityInputEl = document.getElementById('quantityInput');
    const salesFormEl = document.getElementById('salesForm');
    const tableBodyEl = document.getElementById('salesTableBody');

    
    function loadSalesPageData() {
      
      fetch(`${API_URL}/products`) 
        .then(res => res.json())
        .then(products => {
          productSelectEl.innerHTML = ''; 
          
          products.forEach(p => {
            const option = document.createElement('option');
            option.value = p.id;
            option.innerText = `${p.name} (Stock: ${p.quantity})`;
            productSelectEl.appendChild(option);
          });
        })
        .catch(err => console.error("Error loading products inventory list:", err));

      
      fetch(`${API_URL}/sales`) 
        .then(res => res.json())
        .then(salesHistory => {
          tableBodyEl.innerHTML = ''; 
          
          salesHistory.forEach(sale => {
            const row = document.createElement('tr');
            row.innerHTML = `
              <td>${sale.product_id}</td>
              <td>${sale.quantity_sold}</td>
              <td>Ksh ${parseFloat(sale.total_profit || 0).toFixed(2)}</td>
            `;
            tableBodyEl.appendChild(row);
          });
        })
        .catch(err => console.error("Error loading history list records:", err));
    }

    
    salesFormEl.addEventListener('submit', function(e) {
      e.preventDefault(); 

      const payload = {
        product_id: parseInt(productSelectEl.value),
        quantity_sold: parseInt(quantityInputEl.value)
      };

      fetch(`${API_URL}/sales`, { 
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload)
      })
      .then(res => res.json())
      .then(() => {
        alert("Cash sale logged and inventory updated!");
        quantityInputEl.value = "1"; 
        loadSalesPageData();        
      })
      .catch(err => console.error("Error logging cash sale record:", err));
    });
    document.addEventListener('DOMContentLoaded', loadSalesPageData);








    const creditFormEl = document.getElementById('creditForm');
    const customerNameEl = document.getElementById('customerName');
    const amountOwedEl = document.getElementById('amountOwed');
    const itemsBorrowedEl = document.getElementById('itemsBorrowed');
    const tableBodyEl = document.getElementById('creditsTableBody');

    
    function loadCredits() {
      fetch(`${API_URL}/credits`) 
        .then(res => res.json())
        .then(data => {
          tableBodyEl.innerHTML = '';

          data.forEach(c => {
            const row = document.createElement('tr');
            row.innerHTML = `
              <td>${c.cust_name}</td>
              <td>${c.items_borrowed}</td>
              <td>Ksh ${parseFloat(c.amount_owed || 0).toFixed(2)}</td>
              <td>
                <span>${c.payment_status}</span>
              </td>
            `;
            tableBodyEl.appendChild(row);
          });
        })
        .catch(err => console.error("Error fetching credit entries:", err));
    }

    
    creditFormEl.addEventListener('submit', function(e) {
      e.preventDefault();

      const payload = {
        cust_name: customerNameEl.value,
        amount_owed: parseFloat(amountOwedEl.value),
        payment_status: 'Pending',
        items_borrowed: itemsBorrowedEl.value
      };

      fetch(`${API_URL}/credits`, { 
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload)
      })
      .then(res => res.json())
      .then(() => {
        alert("Debtor registered in credit registry!");
        creditFormEl.reset(); 
        loadCredits();       
      })
      .catch(err => console.error("Error logging credit entry:", err));
    });

    document.addEventListener('DOMContentLoaded', loadCredits);

