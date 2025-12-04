// Existing function: registerUser
async function registerUser(e) {
  e.preventDefault();
  const name = document.getElementById('regName').value;
  const mobile = document.getElementById('regMobile').value;
  const email = document.getElementById('regEmail').value;

  try {
    const response = await fetch('http://127.0.0.1:3000/register', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({ name, mobile, email })
    });

    if (!response.ok) {
      throw new Error('Registration failed');
    }

    const data = await response.json();
    alert('Registration successful! Please login.');

    // *** MODIFIED: Switch to Login form (slide back) ***
    showLoginPanel();

    // Optionally clear the register form
    document.getElementById('regName').value = '';
    document.getElementById('regMobile').value = '';
    document.getElementById('regEmail').value = '';

  } catch (error) {
    alert('Error registering user: ' + error.message);
  }

  return false;
}

// Existing function: loginUser
async function loginUser(e) {
  e.preventDefault();
  const mobile = document.getElementById('loginMobile').value;

  try {
    // Generate OTP via API (which checks if user exists)
    await generateOtp();

  } catch (error) {
    alert('Error during login: ' + error.message);
    return false;
  }

  return false;
}



// Existing function: logout
function logout() {
  alert('Logged out successfully!');
  localStorage.clear(); // Clear all localStorage data
  window.location.href = '/login'; // Redirect to login page
}

// --- NEW PROFILE FUNCTIONS ---

// Function to load profile data when the profile page opens
function loadProfile() {
    // Get user data from localStorage (now includes all fields)
    const user = JSON.parse(localStorage.getItem('user')) || {};

    // Check if the form elements exist (only on profile.html)
    if (document.getElementById('profileForm')) {
        document.getElementById('profileName').value = user.name || '';
        document.getElementById('profileMobile').value = user.mobile || '';
        document.getElementById('profileEmail').value = user.email || '';
        document.getElementById('profileDOB').value = user.dob || '';
        document.getElementById('profileGender').value = user.gender || '';
    }
}

// Function to handle profile update
async function updateProfile(e) {
    e.preventDefault();

    const user = JSON.parse(localStorage.getItem('user')) || {};
    const mobile = user.mobile;

    const updatedProfileData = {
        mobile: mobile,
        name: document.getElementById('profileName').value,
        dob: document.getElementById('profileDOB').value,
        gender: document.getElementById('profileGender').value
    };

    try {
    const response = await fetch('http://127.0.0.1:3000/update-profile', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(updatedProfileData)
        });

        if (!response.ok) {
            throw new Error('Profile update failed');
        }

        const data = await response.json();
        // Update localStorage with the updated user from server
        localStorage.setItem('user', JSON.stringify(data.user));

        alert('Profile Updated Successfully!');
    } catch (error) {
        alert('Error updating profile: ' + error.message);
    }

    return false;
}

// --- NEW FORM SWITCHING LOGIC (For Sliding Animation) ---

// Get the main container for animation
const mainContainer = document.querySelector('.login-main');

// Function to show the Register form (Slides to the left)
function showRegisterPanel(e) {
    if (e) e.preventDefault();
    if (mainContainer) {
        mainContainer.classList.add('register-active');
        document.title = 'Cafe Zone | Register'; // Change page title dynamically
    }
}

// Function to show the Login form (Slides back to the right)
function showLoginPanel(e) {
    if (e) e.preventDefault();
    if (mainContainer) {
        mainContainer.classList.remove('register-active');
        document.title = 'Cafe Zone | Login'; // Change page title dynamically
    }
}


// Function to toggle the navigation menu
function toggleNavMenu() {
    const navMenu = document.getElementById('navMenu');
    if (navMenu) {
        navMenu.classList.toggle('active');
    }
}

// Global variable to store timer interval ID
let otpTimerInterval;

// Function to generate OTP (API call)
async function generateOtp() {
  const mobile = document.getElementById('loginMobile').value;

  try {
    const response = await fetch('http://127.0.0.1:3000/login', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({ mobile: mobile })
    });

    if (!response.ok) {
      throw new Error('Failed to send login OTP');
    }

    const data = await response.json();
    localStorage.setItem('otpId', data.otpId);
    localStorage.setItem('otpExpiry', Date.now() + 120000); // 2 minutes

    document.getElementById('otpMessage').textContent = `OTP sent successfully, your OTP is ${data.otp}`;

    // Show OTP section
    document.getElementById('otpSection').style.display = 'block';
    document.getElementById('sendOtpBtn').style.display = 'none';

    // Start timer
    startTimer();
  } catch (error) {
    alert('Error sending login OTP: ' + error.message);
  }
}

// Function to start OTP timer
function startTimer() {
  // Clear any existing timer
  if (otpTimerInterval) {
    clearInterval(otpTimerInterval);
  }

  let timeLeft = 120; // 2 minutes
  const timerDisplay = document.getElementById('timerDisplay');
  const resendBtn = document.getElementById('resendOtpBtn');

  otpTimerInterval = setInterval(() => {
    const minutes = Math.floor(timeLeft / 60);
    const seconds = timeLeft % 60;
    timerDisplay.textContent = `Time remaining: ${minutes}:${seconds.toString().padStart(2, '0')}`;
    timeLeft--;

    if (timeLeft < 0) {
      clearInterval(otpTimerInterval);
      timerDisplay.textContent = 'OTP expired!';
      resendBtn.style.display = 'block';
    }
  }, 1000);
}

// Function to resend OTP
function resendOtp() {
  generateOtp();
  document.getElementById('resendOtpBtn').style.display = 'none';
}

// Function to show intermediate popup
function showIntermediatePopup() {
  const intermediatePopup = document.getElementById('intermediatePopup');
  const intermediateOkBtn = document.getElementById('intermediateOkBtn');
  const intermediateCancelBtn = document.getElementById('intermediateCancelBtn');

  if (intermediatePopup && intermediateOkBtn && intermediateCancelBtn) {
    intermediatePopup.style.display = 'flex';

    // Add event listeners
    intermediateOkBtn.addEventListener('click', () => {
      intermediatePopup.style.display = 'none';
      showDietPopup();
    });
    intermediateCancelBtn.addEventListener('click', () => {
      intermediatePopup.style.display = 'none';
      localStorage.removeItem('dietPreference');
      loadFoodItems();
    });
  }
}

// Function to show diet popup with smooth animation
function showDietPopup() {
  const dietPopup = document.getElementById('dietPopup');
  const dietBtn = document.getElementById('dietBtn');
  const nonDietBtn = document.getElementById('nonDietBtn');
  const cancelBtn = document.getElementById('cancelBtn');

  if (dietPopup && dietBtn && nonDietBtn && cancelBtn) {
    // Reset animation by removing and re-adding the class
    dietPopup.style.display = 'flex';
    dietPopup.classList.remove('popup-overlay');
    void dietPopup.offsetWidth; // Trigger reflow
    dietPopup.classList.add('popup-overlay');

    // Add event listeners for diet buttons with animation
    dietBtn.addEventListener('click', () => handleDietSelection('diet'));
    nonDietBtn.addEventListener('click', () => handleDietSelection('non-diet'));
    cancelBtn.addEventListener('click', () => handleDietSelection('cancel'));
  }
}

// Function to hide popup with fade out animation
function hidePopup(popupId) {
  const popup = document.getElementById(popupId);
  if (popup) {
    popup.style.animation = 'fadeOut 0.3s ease forwards';
    setTimeout(() => {
      popup.style.display = 'none';
      popup.style.animation = '';
    }, 300);
  }
}

// Function to handle diet selection
function handleDietSelection(dietPreference) {
  localStorage.setItem('dietPreference', dietPreference);
  document.getElementById('dietPopup').style.display = 'none';
  loadFoodItems();
}

// Function to verify OTP (API call)
async function verifyOtp() {
  console.log('verifyOtp called');
  // Only allow OTP verification on login page (served at / or /login)
  if (window.location.pathname !== '/' && !window.location.pathname.includes('login.html')) {
    console.log('Not on login page');
    return;
  }

  const enteredOtp = document.getElementById('otpInput').value.trim();
  console.log('Entered OTP:', enteredOtp);
  const otpId = localStorage.getItem('otpId');
  console.log('OTP ID:', otpId);
  const expiry = parseInt(localStorage.getItem('otpExpiry'));
  console.log('Expiry:', expiry, 'Current time:', Date.now());

  if (Date.now() > expiry) {
    alert('OTP expired! Please resend.');
    return;
  }

  try {
    const response = await fetch('http://127.0.0.1:3000/verify-login-otp', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({ otpId: otpId, otp: enteredOtp })
    });

    const data = await response.json();

    if (!response.ok) {
      throw new Error(data.error || 'Verification failed');
    }

    if (data.success) {
      // Fetch user data after successful login
      const mobile = document.getElementById('loginMobile').value;
      const checkResponse = await fetch('http://127.0.0.1:3000/check-user', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({ mobile })
      });

      if (checkResponse.ok) {
        const checkData = await checkResponse.json();
        if (checkData.exists) {
          localStorage.setItem('user', JSON.stringify(checkData.user));
        }
      }

      // Always redirect to cafeteria after successful login
      window.location.href = '/cafeteria';
    } else {
      alert('Invalid OTP!');
    }
  } catch (error) {
    alert('Error verifying OTP: ' + error.message);
  }
}





// Global cart storage
let cart = JSON.parse(localStorage.getItem('cart')) || [];

// Function to save cart to localStorage
function saveCart() {
    localStorage.setItem('cart', JSON.stringify(cart));
}

// Function to update cart count display (if you have a cart icon)
function updateCartCount() {
    const cartCount = document.getElementById('cart-count');
    if (cartCount) {
        const totalItems = cart.reduce((sum, item) => sum + item.quantity, 0);
        cartCount.textContent = totalItems;
    }
}

// Function to add item to cart
function addToCart(itemId, name, price, image_url, protein, carbs, fats, calories) {
    const itemName = name || 'Item';
    const existingItem = cart.find(item => item.id === itemId);
    if (existingItem) {
        existingItem.quantity += 1;
    } else {
        cart.push({
            id: itemId,
            name: itemName,
            price: parseFloat(price),
            image_url: image_url,
            protein: parseFloat(protein || 0),
            carbs: parseFloat(carbs || 0),
            fats: parseFloat(fats || 0),
            calories: parseFloat(calories || 0),
            quantity: 1
        });
    }
    saveCart();
    updateCartCount();
    alert(`${itemName} added to cart!`);
}

// Function to increase quantity
function increaseQuantity(itemId) {
    const quantityElement = document.getElementById(`quantity-${itemId}`);
    let quantity = parseInt(quantityElement.textContent);
    quantityElement.textContent = quantity + 1;
}

// Function to decrease quantity
function decreaseQuantity(itemId) {
    const quantityElement = document.getElementById(`quantity-${itemId}`);
    let quantity = parseInt(quantityElement.textContent);
    if (quantity > 1) {
        quantityElement.textContent = quantity - 1;
    }
}

// Function to create nutrition chart
function createNutritionChart(canvasId, protein, carbs, fats, calories) {
    const ctx = document.getElementById(canvasId);
    if (!ctx) return;

    new Chart(ctx, {
        type: 'pie',
        data: {
            labels: ['Protein', 'Carbs', 'Fats'],
            datasets: [{
                data: [protein, carbs, fats],
                backgroundColor: [
                    '#FF6384', // Protein - Red
                    '#36A2EB', // Carbs - Blue
                    '#FFCE56'  // Fats - Yellow
                ],
                borderWidth: 1
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    position: 'bottom',
                    labels: {
                        boxWidth: 12,
                        font: {
                            size: 10
                        }
                    }
                },
                tooltip: {
                    callbacks: {
                        label: function(context) {
                            const label = context.label || '';
                            const value = context.parsed || 0;
                            const total = context.dataset.data.reduce((a, b) => a + b, 0);
                            const percentage = Math.round((value / total) * 100);
                            return `${label}: ${value}g (${percentage}%)`;
                        }
                    }
                }
            }
        }
    });
}

// Function to load food items with robust fallbacks and display in menu-grid
async function loadFoodItems() {
    try {
        let foodItems = [];

        // Backend first (original behavior)
        try {
            const response = await fetch('http://127.0.0.1:3000/food-items');
            if (response.ok) {
                foodItems = await response.json();
                try { localStorage.setItem('cachedFoodItems', JSON.stringify(foodItems)); } catch (_) {}
            }
        } catch (_) { /* ignore */ }

        // CSV fallback
        if (!foodItems || foodItems.length === 0) {
            const csvItems = await loadItemsFromCsvPaths(['FoodItem_export_clean.csv', 'fooditem_export.csv','item_export.csv']);
            if (csvItems && csvItems.length) foodItems = csvItems;
        }

        // Try cached
        if (!foodItems || foodItems.length === 0) {
            const cached = JSON.parse(localStorage.getItem('cachedFoodItems') || '[]');
            if (cached.length) foodItems = cached;
        }

        // Built-in sample to ensure page never looks empty
        if (!foodItems || foodItems.length === 0) {
            foodItems = [
                { id:'sample1', name:'Sprouts Chaat', price:110, image_url:'images/pizza1.jpeg', protein:18, carbs:28, fats:6, calories:230, category:'diet', description:'Light and protein rich.' },
                { id:'sample2', name:'Paneer Tikka', price:280, image_url:'images/indian.jpeg', protein:24, carbs:45, fats:28, calories:550, category:'diet', description:'Creamy classic.' },
                { id:'sample3', name:'Aloo Tikki Burger', price:80, image_url:'images/burger1.jpeg', protein:10, carbs:52, fats:20, calories:430, category:'non-diet', description:'Tasty treat.' }
            ];
        }

        // Ensure image URLs are absolute paths
        foodItems.forEach(item => {
            if (!item.image_url.startsWith('/')) {
                item.image_url = '/static/' + item.image_url;
            }
        });

        // Filter based on preference
        const dietPreference = localStorage.getItem('dietPreference');
        if (dietPreference === 'diet') {
            foodItems = foodItems.filter(item => (item.category||'').toLowerCase() === 'diet');
        } else if (dietPreference === 'non-diet') {
            foodItems = foodItems.filter(item => (item.category||'').toLowerCase() === 'non-diet');
        }

        const menuGrid = document.querySelector('.menu-grid');
        if (!menuGrid) return;
        menuGrid.innerHTML = '';

        // Render cards
        foodItems.forEach((item, index) => {
            const menuItem = document.createElement('div');
            menuItem.className = 'menu-item menu-card';

            const chartId = `nutrition-chart-${index}`;

            menuItem.innerHTML = `
                <div class="image-block">
                    <img src="${item.image_url}" alt="${item.name}" class="item-image">
                </div>
                <div class="item-details">
                    <div class="title-rating">
                        <h3 class="item-title">${item.name}</h3>
                        <div class="item-rating">
                            <span class="star-icon">&#9733;</span> 4.5
                        </div>
                    </div>
                    <p class="item-description">${item.description || ''}</p>
                    <div class="nutrition-info">
                        <div class="nutrition-values">
                            <span class="nutrition-item">Protein: ${item.protein || 0}g</span>
                            <span class="nutrition-item">Carbs: ${item.carbs || 0}g</span>
                            <span class="nutrition-item">Fats: ${item.fats || 0}g</span>
                            <span class="nutrition-item">Calories: ${item.calories || 0}</span>
                        </div>
                        <div class="nutrition-chart">
                            <canvas id="${chartId}" width="100" height="100"></canvas>
                        </div>
                    </div>
                    <p class="item-price">₹${item.price}</p>
                    <div class="quantity-controls">
                        <button class="quantity-btn" onclick="decreaseQuantity('${item.id}')">-</button>
                        <span class="quantity-display" id="quantity-${item.id}">1</span>
                        <button class="quantity-btn" onclick="increaseQuantity('${item.id}')">+</button>
                    </div>
                    <button class="add-to-cart-btn" onclick="addToCart('${item.id}', '${item.name}', '${item.price}', '${item.image_url}', '${item.protein}', '${item.carbs}', '${item.fats}', '${item.calories}')">Add to Cart</button>
                </div>
            `;

            menuGrid.appendChild(menuItem);
            setTimeout(() => {
                createNutritionChart(chartId, parseInt(item.protein||0), parseInt(item.carbs||0), parseInt(item.fats||0), parseInt(item.calories||0));
            }, 50);
        });

        updateCartCount();
    } catch (error) {
        console.error('Error loading food items (handled gracefully):', error);
        // Do not alert; page already rendered with fallbacks above
    }
}

// Function to load cart page
function loadCartPage() {
    const cartItems = document.getElementById('cart-items');
    const cartSummary = document.getElementById('cart-summary');
    const emptyCart = document.getElementById('empty-cart');

    cart = JSON.parse(localStorage.getItem('cart')) || [];

    if (cart.length === 0) {
        cartItems.style.display = 'none';
        cartSummary.style.display = 'none';
        emptyCart.style.display = 'block';
        return;
    }

    emptyCart.style.display = 'none';
    cartItems.style.display = 'block';
    cartSummary.style.display = 'block';

    // Render cart items
    cartItems.innerHTML = cart.map(item => `
        <div class="cart-item">
            <img src="${item.image_url || '/static/images/default-food.jpg'}" alt="${item.name}" class="cart-item-image">
            <div class="cart-item-details">
                <h4>${item.name}</h4>
                <p>₹${item.price} each</p>
                <div class="cart-quantity-controls">
                    <button class="quantity-btn" onclick="updateCartQuantity('${item.id}', -1)">-</button>
                    <span class="quantity-display">${item.quantity}</span>
                    <button class="quantity-btn" onclick="updateCartQuantity('${item.id}', 1)">+</button>
                </div>
            </div>
            <div class="cart-item-total">
                <p>₹${(item.price * item.quantity).toFixed(2)}</p>
                <button class="remove-btn" onclick="removeFromCart('${item.id}')">Remove</button>
            </div>
        </div>
    `).join('');

    // Render cart summary with GST (18%)
    const totalItems = cart.reduce((sum, item) => sum + item.quantity, 0);
    const subTotal = cart.reduce((sum, item) => sum + (item.price * item.quantity), 0);
    const gst = subTotal * 0.18;
    const grandTotal = subTotal + gst;

    // Calculate nutritional totals
    const nutritionTotals = cart.reduce((acc, item) => {
        acc.protein += (item.protein || 0) * item.quantity;
        acc.carbs += (item.carbs || 0) * item.quantity;
        acc.fats += (item.fats || 0) * item.quantity;
        acc.calories += (item.calories || 0) * item.quantity;
        return acc;
    }, { protein: 0, carbs: 0, fats: 0, calories: 0 });

    cartSummary.innerHTML = `
        <h3>Order Summary</h3>
        <div class="summary-row"><span>Subtotal</span><span>₹${subTotal.toFixed(2)}</span></div>
        <div class="summary-row"><span>GST (18%)</span><span>₹${gst.toFixed(2)}</span></div>
        <div class="summary-row total"><span>Total</span><span>₹${grandTotal.toFixed(2)}</span></div>
        <div class="nutrition-summary">
            <h4>Nutritional Summary</h4>
            <div class="nutrition-row"><span>Protein</span><span>${nutritionTotals.protein.toFixed(1)}g</span></div>
            <div class="nutrition-row"><span>Carbs</span><span>${nutritionTotals.carbs.toFixed(1)}g</span></div>
            <div class="nutrition-row"><span>Fats</span><span>${nutritionTotals.fats.toFixed(1)}g</span></div>
            <div class="nutrition-row"><span>Calories</span><span>${Math.round(nutritionTotals.calories)}</span></div>
        </div>
        <button class="checkout-btn" onclick="proceedToPayment()">Proceed to Payment</button>
        <div style="font-size:12px;color:#777;margin-top:6px;">Payment will be processed automatically • Secure checkout</div>
    `;

    updateCartCount();

    // Render nutrition analytics
    renderCartNutrition();
}

// Function to load cart count on all pages
function loadCartCount() {
    updateCartCount();
}

// Function to update cart quantity
function updateCartQuantity(itemId, change) {
    const item = cart.find(item => item.id === itemId);
    if (item) {
        item.quantity += change;
        if (item.quantity <= 0) {
            removeFromCart(itemId);
            return;
        }
        saveCart();
        loadCartPage();
    }
}

// Function to remove item from cart
function removeFromCart(itemId) {
    cart = cart.filter(item => item.id !== itemId);
    saveCart();
    loadCartPage();
}

// Function to proceed to payment
function showProcessingOverlay() {
    // Avoid duplicating
    if (document.getElementById('processingOverlay')) return;
    const overlay = document.createElement('div');
    overlay.id = 'processingOverlay';
    overlay.style.position = 'fixed';
    overlay.style.inset = '0';
    overlay.style.background = 'rgba(0,0,0,0.35)';
    overlay.style.zIndex = '9999';
    overlay.style.display = 'flex';
    overlay.style.alignItems = 'center';
    overlay.style.justifyContent = 'center';

    const card = document.createElement('div');
    card.style.background = '#fff';
    card.style.borderRadius = '14px';
    card.style.boxShadow = '0 10px 30px rgba(0,0,0,0.2)';
    card.style.width = '520px';
    card.style.maxWidth = '92%';
    card.style.padding = '26px';
    card.style.textAlign = 'center';

    card.innerHTML = `
        <div style="width:64px;height:64px;margin:0 auto 12px auto;border-radius:50%;background:#e6f4ea;display:flex;align-items:center;justify-content:center;font-size:26px;color:#2e7d32;">↗</div>
        <div style="font-weight:800;color:#7a3b41;font-size:20px;margin-bottom:6px;">Processing Your Order</div>
        <div style="color:#4b5563;margin-bottom:14px;">Generating your personalized diet plan...</div>
        <div style="height:8px;background:#eef2f7;border-radius:999px;overflow:hidden;">
            <div id="processingBar" style="height:100%;width:10%;background:#2e7d32;border-radius:999px;transition:width 0.25s ease;"></div>
        </div>
    `;
    overlay.appendChild(card);
    document.body.appendChild(overlay);

    // Animate bar
    let pct = 10;
    const timer = setInterval(() => {
        pct = Math.min(95, pct + Math.floor(Math.random()*15)+5);
        const bar = document.getElementById('processingBar');
        if (bar) bar.style.width = pct + '%';
    }, 250);

    return () => { clearInterval(timer); document.body.removeChild(overlay); };
}

function proceedToPayment() {
    const hide = showProcessingOverlay();
    setTimeout(() => {
        hide && hide();
        window.location.href = '/payment';
    }, 1600);
}

// Function to load payment page
function loadPaymentPage() {
    const orderSummary = document.getElementById('order-summary');
    cart = JSON.parse(localStorage.getItem('cart')) || [];

    if (cart.length === 0) {
        alert('Your cart is empty!');
        window.location.href = 'cart.html';
        return;
    }

    const totalItems = cart.reduce((sum, item) => sum + item.quantity, 0);
    const totalPrice = cart.reduce((sum, item) => sum + (item.price * item.quantity), 0);
    const deliveryFee = 50;
    const grandTotal = totalPrice + deliveryFee;

    orderSummary.innerHTML = `
        <h3>Order Summary</h3>
        <div class="order-items">
            ${cart.map(item => `
                <div class="order-item">
                    <span>${item.name} x${item.quantity}</span>
                    <span>₹${(item.price * item.quantity).toFixed(2)}</span>
                </div>
            `).join('')}
        </div>
        <div class="order-total">
            <div class="summary-row">
                <span>Subtotal:</span>
                <span>₹${totalPrice.toFixed(2)}</span>
            </div>
            <div class="summary-row">
                <span>Delivery Fee:</span>
                <span>₹${deliveryFee.toFixed(2)}</span>
            </div>
            <div class="summary-row total">
                <span>Total:</span>
                <span>₹${grandTotal.toFixed(2)}</span>
            </div>
        </div>
    `;

    updateCartCount();
}

// Function to toggle payment form based on selected method
function togglePaymentForm() {
    const selectedMethod = document.querySelector('input[name="paymentMethod"]:checked').value;
    const cardForm = document.getElementById('card-payment-form');
    const codPayment = document.getElementById('cod-payment');

    if (selectedMethod === 'card') {
        cardForm.style.display = 'block';
        codPayment.style.display = 'none';
    } else {
        cardForm.style.display = 'none';
        codPayment.style.display = 'block';
    }
}

// Function to process card payment
async function processCardPayment(event) {
    event.preventDefault();

    // Basic validation
    const cardNumber = document.getElementById('cardNumber').value;
    const expiryDate = document.getElementById('expiryDate').value;
    const cvv = document.getElementById('cvv').value;
    const cardName = document.getElementById('cardName').value;

    if (!cardNumber || !expiryDate || !cvv || !cardName) {
        alert('Please fill in all payment details.');
        return;
    }

    // Get user details
    const user = JSON.parse(localStorage.getItem('user')) || {};
    const totalAmount = calculateTotal();

    // Save order before clearing cart and generate invoice
    await saveOrder('paid', 'Card Payment');
    await generateAndDownloadInvoice('Card Payment', user.name, user.mobile);

    // Simulate payment processing
    alert('Card payment successful! Your order has been placed. Invoice downloaded.');

    // Clear cart
    localStorage.removeItem('cart');
    cart = [];

    // Redirect to cafeteria
    window.location.href = 'cafeteria.html';
}

// Function to process cash on delivery
async function processCodPayment() {
    // Confirm COD order
    if (confirm('Confirm your Cash on Delivery order? You will pay ₹' + calculateTotal() + ' when the order is delivered.')) {
        // Get user details
        const user = JSON.parse(localStorage.getItem('user')) || {};
        const totalAmount = calculateTotal();

        // Save order and Generate invoice
        await saveOrder('paid', 'Cash on Delivery');
        await generateAndDownloadInvoice('Cash on Delivery', user.name, user.mobile);

        alert('Cash on Delivery order confirmed! Your order will be delivered in 30-45 minutes. Invoice downloaded.');

        // Clear cart
        localStorage.removeItem('cart');
        cart = [];

        // Redirect to cafeteria
        window.location.href = 'cafeteria.html';
    }
}

// Function to generate and download invoice
async function generateAndDownloadInvoice(paymentMethod, customerName, customerMobile) {
    try {
        const response = await fetch('http://127.0.0.1:3000/generate-invoice', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                orderItems: cart,
                totalAmount: calculateTotal(),
                paymentMethod: paymentMethod,
                customerName: customerName,
                customerMobile: customerMobile
            })
        });

        if (!response.ok) {
            throw new Error('Failed to generate invoice');
        }

        const data = await response.json();

        // Create a download link for the PDF
        const link = document.createElement('a');
        link.href = 'data:application/pdf;base64,' + data.pdf;
        link.download = `HangOut Cafe_Invoice_${data.invoiceNumber}.pdf`;
        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link);

    } catch (error) {
        console.error('Error generating invoice:', error);
        alert('Failed to generate invoice. Please try again.');
    }
}

// Helper function to calculate total
function calculateTotal() {
    cart = JSON.parse(localStorage.getItem('cart')) || [];
    const totalPrice = cart.reduce((sum, item) => sum + (item.price * item.quantity), 0);
    return (totalPrice + 50).toFixed(2); // Including delivery fee
}

// -------- Orders Storage & Rendering --------
async function saveOrder(status, paymentMethod) {
    const user = JSON.parse(localStorage.getItem('user')) || {};
    const existing = JSON.parse(localStorage.getItem('orders') || '[]');

    const orderNumber = '#'+Math.floor(Math.random()*1e10).toString(16);
    const totals = cart.reduce((acc, it) => {
        acc.itemsTotal += it.price * it.quantity;
        acc.protein += (it.protein||0) * it.quantity;
        acc.carbs += (it.carbs||0) * it.quantity;
        acc.fats += (it.fats||0) * it.quantity;
        acc.calories += (it.calories||0) * it.quantity;
        return acc;
    }, { itemsTotal:0, protein:0, carbs:0, fats:0, calories:0 });

    const order = {
        id: orderNumber,
        date: new Date().toISOString(),
        status: status,
        paymentMethod,
        items: cart.map(i => ({ name: i.name, quantity: i.quantity, price: i.price })),
        metrics: totals,
        total: (totals.itemsTotal + 50) // add delivery like payment page
    };

    existing.unshift(order);
    localStorage.setItem('orders', JSON.stringify(existing));
}

function loadOrdersPage() {
    const list = document.getElementById('orders-list');
    const empty = document.getElementById('orders-empty');

    const orders = JSON.parse(localStorage.getItem('orders') || '[]');
    if (!orders.length) {
        if (empty) empty.style.display = 'block';
        return;
    }
    if (empty) empty.style.display = 'none';

    if (!list) return;

    list.innerHTML = orders.map(o => `
        <div class="order-card">
            <div class="order-bar">
                <div>Order ${o.id}<div style="font-size:12px;color:#7a8188;">${new Date(o.date).toLocaleDateString()}</div></div>
                <span class="order-status">${o.status}</span>
            </div>
            <div class="order-body">
                <div class="order-items-list">${o.items.map(it => `${it.name} x${it.quantity}`).join('<br>')}</div>
                <div class="order-metrics">
                    <div class="metric-box"><h5>Protein</h5><div class="metric-val">${o.metrics.protein.toFixed(1)}g</div></div>
                    <div class="metric-box"><h5>Carbs</h5><div class="metric-val">${o.metrics.carbs.toFixed(1)}g</div></div>
                    <div class="metric-box"><h5>Fats</h5><div class="metric-val">${o.metrics.fats.toFixed(1)}g</div></div>
                    <div class="metric-box"><h5>Calories</h5><div class="metric-val">${Math.round(o.metrics.calories)}</div></div>
                    <div class="metric-box"><h5>Total</h5><div class="metric-val">₹${o.total.toFixed(2)}</div></div>
                </div>
            </div>
            <div class="order-footer">
                <button class="invoice-btn" onclick="alert('Invoice already downloaded during checkout.')">View Invoice</button>
            </div>
        </div>
    `).join('');
}

// --- Cart nutrition rendering ---
function renderCartNutrition() {
    const section = document.getElementById('nutrition-section');
    if (!section) return;

    cart = JSON.parse(localStorage.getItem('cart')) || [];
    if (cart.length === 0) {
        section.style.display = 'none';
        return;
    }

    const totals = cart.reduce((acc, item) => {
        acc.protein += (item.protein || 0) * item.quantity;
        acc.carbs += (item.carbs || 0) * item.quantity;
        acc.fats += (item.fats || 0) * item.quantity;
        acc.calories += (item.calories || 0) * item.quantity;
        return acc;
    }, { protein: 0, carbs: 0, fats: 0, calories: 0 });

    section.style.display = 'block';

    const cards = document.getElementById('nutrition-cards');
    if (cards) {
        cards.innerHTML = `
            <div class="nutrition-card"><h4>Protein</h4><div class="nutrition-value">${totals.protein.toFixed(1)}g</div></div>
            <div class="nutrition-card"><h4>Carbs</h4><div class="nutrition-value">${totals.carbs.toFixed(1)}g</div></div>
            <div class="nutrition-card"><h4>Fats</h4><div class="nutrition-value">${totals.fats.toFixed(1)}g</div></div>
            <div class="nutrition-card"><h4>Calories</h4><div class="nutrition-value">${Math.round(totals.calories)}</div></div>
        `;
    }

    // Draw charts
    const pieCanvas = document.getElementById('macroPieChart');
    const barCanvas = document.getElementById('macroBarChart');
    if (pieCanvas) {
        new Chart(pieCanvas, {
            type: 'pie',
            data: {
                labels: ['Protein', 'Carbs', 'Fats'],
                datasets: [{
                    data: [totals.protein, totals.carbs, totals.fats],
                    backgroundColor: ['#2e7d32', '#7a3b41', '#f39c12']
                }]
            },
            options: { responsive: true, plugins: { legend: { position: 'bottom' } } }
        });
    }
    if (barCanvas) {
        new Chart(barCanvas, {
            type: 'bar',
            data: {
                labels: ['Protein', 'Carbs', 'Fats'],
                datasets: [{
                    label: 'Macronutrient Grams',
                    data: [totals.protein, totals.carbs, totals.fats],
                    backgroundColor: ['#2e7d32', '#7a3b41', '#f39c12']
                }]
            },
            options: { responsive: true, scales: { y: { beginAtZero: true } } }
        });
    }
}

// --- CSV helper (quoted fields + multi-filename support) ---
function csvSafeSplit(line) {
    const parts = [];
    let cur = '';
    let inQ = false;
    for (let i = 0; i < line.length; i++) {
        const ch = line[i];
        if (ch === '"') {
            if (inQ && line[i+1] === '"') { cur += '"'; i++; }
            else { inQ = !inQ; }
        } else if (ch === ',' && !inQ) {
            parts.push(cur.trim()); cur = '';
        } else { cur += ch; }
    }
    parts.push(cur.trim());
    return parts.map(v => v.replace(/^"|"$/g, ''));
}

async function loadItemsFromCsv(csvPath) {
    try {
        const res = await fetch(csvPath, { cache: 'no-store' });
        if (!res.ok) return null;
        const text = await res.text();
        const lines = text.split(/\r?\n/).filter(l => l.trim().length > 0);
        if (lines.length < 2) return null;
        const headers = csvSafeSplit(lines[0]).map(h => h.trim());
        const rows = lines.slice(1).map(line => {
            const cols = csvSafeSplit(line);
            const obj = {};
            headers.forEach((h, i) => obj[h] = (cols[i] || '').trim());
            return obj;
        });
        return rows.map(r => ({
            id: r.id || r.ID || r.slug || r.name,
            name: r.name || r.title,
            description: r.description || r.desc || '',
            price: parseFloat(r.price || r.cost || 0),
            image_url: r.image_url || r.image || r.photo || r.imageUrl || '',
            protein: parseFloat(r.protein || r.proteins || 0),
            carbs: parseFloat(r.carbs || r.carb || 0),
            fats: parseFloat(r.fats || r.fat || 0),
            calories: parseFloat(r.calories || r.kcal || 0),
            category: (r.category || r.type || '').toLowerCase()
        }));
    } catch (_) {
        return null;
    }
}

async function loadItemsFromCsvPaths(paths) {
    for (const p of paths) {
        const items = await loadItemsFromCsv(p);
        if (items && items.length) return items;
    }
    return null;
}

// --- AI Recommendations ---
async function loadAIRecommendations() {
    const body = document.getElementById('aiRecoBody');
    const cardsContainer = document.getElementById('aiRecoCards');
    const loading = document.getElementById('aiRecoLoading');
    const tag = document.getElementById('aiRecoTag');
    if (!body || !cardsContainer) return;

    loading.style.display = 'block';
    cardsContainer.style.display = 'none';

    try {
        // Backend first (original behavior)
        let items = [];
        try {
            const res = await fetch('http://127.0.0.1:3000/food-items');
            if (res.ok) {
                items = await res.json();
                try { localStorage.setItem('cachedFoodItems', JSON.stringify(items)); } catch (_) {}
            }
        } catch (_) { /* ignore */ }
        // CSV fallback
        if (!items || items.length === 0) {
            items = await loadItemsFromCsvPaths(['FoodItem_export_clean.csv', 'fooditem_export.csv','item_export.csv']);
        }
        if (!items || items.length === 0) {
            const cached = JSON.parse(localStorage.getItem('cachedFoodItems') || '[]');
            if (cached.length) items = cached;
        }
        if (!items || items.length === 0) {
            // built-in minimal sample so UI never looks empty
            items = [
                { id:'sample1', name:'Sprouts Chaat', price:110, image_url:'images/pizza1.jpeg', protein:18, carbs:28, fats:6, calories:230, category:'diet', description:'Light and protein rich.' },
                { id:'sample2', name:'Paneer Tikka', price:280, image_url:'images/indian.jpeg', protein:24, carbs:45, fats:28, calories:550, category:'diet', description:'Creamy classic.' },
                { id:'sample3', name:'Aloo Tikki Burger', price:80, image_url:'images/burger1.jpeg', protein:10, carbs:52, fats:20, calories:430, category:'non-diet', description:'Tasty treat.' }
            ];
        }
        const pref = localStorage.getItem('dietPreference');
        tag.textContent = pref === 'diet' ? 'Diet picks' : (pref === 'non-diet' ? 'Treat yourself' : 'Balanced');

        // Simple heuristic: Diet -> high protein, Non-diet -> high calories, else top rating proxy by carbs
        if (pref === 'diet') {
            items.sort((a,b) => (parseFloat(b.protein||0)) - (parseFloat(a.protein||0)));
        } else if (pref === 'non-diet') {
            items.sort((a,b) => (parseFloat(b.calories||0)) - (parseFloat(a.calories||0)));
        } else {
            items.sort((a,b) => (parseFloat(b.carbs||0)) - (parseFloat(a.carbs||0)));
        }

        const top = items.slice(0, 5);
        // Ensure image URLs are absolute paths
        top.forEach(it => {
            if (!it.image_url.startsWith('/')) {
                it.image_url = '/static/' + it.image_url;
            }
        });
        cardsContainer.innerHTML = top.map(it => `
            <div class="ai-card">
                <img src="${it.image_url}" alt="${it.name}">
                <div class="ai-card-body">
                    <div style="display:flex;justify-content:space-between;align-items:center;">
                        <strong>${it.name}</strong>
                        <span class="item-price" style="margin:0">₹${it.price}</span>
                    </div>
                    <button class="add-to-cart-btn" style="margin-top:8px" onclick="addToCart('${it.id}','${it.name}','${it.price}','${it.image_url}','${it.protein}','${it.carbs}','${it.fats}','${it.calories}')">Add to Cart</button>
                </div>
            </div>
        `).join('');

        // brief delay to show analyzing
        setTimeout(() => {
            loading.style.display = 'none';
            cardsContainer.style.display = 'grid';
        }, 700);
    } catch(e) {
        loading.textContent = 'Unable to load recommendations.';
    }
}

// Existing DOMContentLoaded logic
document.addEventListener('DOMContentLoaded', () => {
    // Check the URL to only run loadProfile on the profile page
    if (window.location.pathname.includes('profile.html')) {
        // Check if user is logged in
        const user = JSON.parse(localStorage.getItem('user'));
        if (!user) {
            alert('Please login first!');
            window.location.href = 'login.html';
            return;
        }
        loadProfile();
        renderProfileInsights();
    }

    // Load food items on cafeteria page
    if (window.location.pathname.includes('cafeteria')) {
        // Check if user is logged in
        const user = JSON.parse(localStorage.getItem('user'));
        if (!user) {
            alert('Please login first!');
            window.location.href = '/login';
            return;
        }

    // Show welcome popup
    const welcomePopup = document.getElementById('welcomePopup');
    const continueBtn = document.getElementById('continueBtn');

    if (welcomePopup && continueBtn) {
        welcomePopup.style.display = 'flex';

        // Handle continue button to show intermediate popup
        continueBtn.addEventListener('click', () => {
            welcomePopup.style.display = 'none';
            showIntermediatePopup();
        });
    }

        // Render AI recommendations banner
        loadAIRecommendations();

        // Filter chip events
        const filterAll = document.getElementById('filterAll');
        const filterDiet = document.getElementById('filterDiet');
        const filterNon = document.getElementById('filterNonDiet');
        const setActive = (el) => {
            [filterAll, filterDiet, filterNon].forEach(b => b && b.classList.remove('active'));
            el && el.classList.add('active');
        };
        filterAll && filterAll.addEventListener('click', () => { localStorage.removeItem('dietPreference'); setActive(filterAll); loadFoodItems(); loadAIRecommendations(); });
        filterDiet && filterDiet.addEventListener('click', () => { localStorage.setItem('dietPreference','diet'); setActive(filterDiet); loadFoodItems(); loadAIRecommendations(); });
        filterNon && filterNon.addEventListener('click', () => { localStorage.setItem('dietPreference','non-diet'); setActive(filterNon); loadFoodItems(); loadAIRecommendations(); });
    }

    // Load cart page
    if (window.location.pathname.includes('/cart')) {
        loadCartPage();
    }

    // Load payment page
    if (window.location.pathname.includes('/payment')) {
        loadPaymentPage();
    }

    // Load cart count on all pages
    loadCartCount();

    // Attempt AI recos on any page that contains the section
    loadAIRecommendations();

    // NEW: Check if the login page is being loaded and handle URL hash
    // This allows linking to the register form directly or handling browser back/forward
    if (window.location.pathname.includes('login.html') && window.location.hash === '#register') {
        showRegisterPanel();
    }

    // Add event listener to OTP input to handle Enter key
    const otpInput = document.getElementById('otpInput');
    if (otpInput) {
        otpInput.addEventListener('keydown', (e) => {
            if (e.key === 'Enter') {
                e.preventDefault();
                verifyOtp();
            }
        });
    }
});

// Function to clear all orders
function clearAllOrders() {
    if (confirm('Are you sure you want to clear all orders? This action cannot be undone.')) {
        localStorage.removeItem('orders');
        alert('All orders have been cleared.');
        loadOrdersPage(); // Reload the orders page to show empty state
    }
}

// Render profile insights (totals and averages from stored orders)
async function renderProfileInsights() {
    const user = JSON.parse(localStorage.getItem('user')) || {};
    const nameEl = document.getElementById('profileDisplayName');
    const emailEl = document.getElementById('profileDisplayEmail');
    const avatarEl = document.querySelector('.avatar');
    if (nameEl) nameEl.textContent = user.name || 'Guest';
    if (emailEl) emailEl.textContent = user.email || '';
    if (avatarEl) avatarEl.textContent = (user.name || 'A').trim().charAt(0).toUpperCase();

    const orders = JSON.parse(localStorage.getItem('orders') || '[]');
    const totalEl = document.getElementById('totalOrdersCount');
    if (totalEl) totalEl.textContent = orders.length || 0;

    const pref = localStorage.getItem('dietPreference');
    const prefText = document.getElementById('prefText');
    if (prefText) prefText.textContent = pref === 'diet' ? 'Diet' : (pref === 'non-diet' ? 'Non-Diet' : 'Balanced');

    // Fetch login count from server
    try {
        const response = await fetch('http://127.0.0.1:3000/login-count', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ mobile: user.mobile })
        });
        if (response.ok) {
            const data = await response.json();
            const loginEl = document.getElementById('totalLogins');
            if (loginEl) loginEl.textContent = data.loginCount || 0;
        }
    } catch (error) {
        console.error('Error fetching login count:', error);
    }

    if (!orders.length) return;

    const sums = orders.reduce((acc,o)=>{
        acc.protein += o.metrics?.protein || 0;
        acc.carbs += o.metrics?.carbs || 0;
        acc.fats += o.metrics?.fats || 0;
        acc.calories += o.metrics?.calories || 0;
        return acc;
    }, {protein:0,carbs:0,fats:0,calories:0});
    const n = orders.length;
    const set = (id, val, suffix='') => { const el=document.getElementById(id); if(el) el.textContent = val + suffix; };
    set('avgProtein', (sums.protein/n).toFixed(1)+'g');
    set('avgCarbs', (sums.carbs/n).toFixed(1)+'g');
    set('avgFats', (sums.fats/n).toFixed(1)+'g');
    set('avgCalories', Math.round(sums.calories/n));
}
