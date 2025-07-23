
const express = require('express');
const cors = require('cors');
const stripe = require('stripe')(process.env.STRIPE_SECRET_KEY);
const sqlite3 = require('sqlite3').verbose();

const app = express();
app.use(cors());
app.use(express.json());

// Database setup
const db = new sqlite3.Database('./saas_database.db');

db.serialize(() => {
  db.run(`CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    email TEXT UNIQUE,
    subscription_plan TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
  )`);
  
  db.run(`CREATE TABLE IF NOT EXISTS subscriptions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER,
    stripe_subscription_id TEXT,
    plan TEXT,
    status TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
  )`);
});

// API Routes
app.get('/api/user-data', (req, res) => {
  // Simulate user data
  res.json({
    id: 1,
    email: 'user@example.com',
    activeUsers: Math.floor(Math.random() * 1000) + 100,
    revenue: Math.floor(Math.random() * 50000) + 10000,
    growth: Math.floor(Math.random() * 50) + 10
  });
});

app.post('/api/create-subscription', async (req, res) => {
  try {
    const { plan, userId } = req.body;
    
    // Create Stripe subscription
    const subscription = await stripe.subscriptions.create({
      customer: 'cus_example',
      items: [{ price: 'price_' + plan }],
      payment_behavior: 'default_incomplete',
      expand: ['latest_invoice.payment_intent'],
    });
    
    // Store in database
    db.run(`INSERT INTO subscriptions (user_id, stripe_subscription_id, plan, status) 
            VALUES (?, ?, ?, ?)`, 
            [userId, subscription.id, plan, subscription.status]);
    
    res.json({ success: true, subscriptionId: subscription.id });
  } catch (error) {
    res.status(500).json({ error: error.message });
  }
});

const PORT = process.env.PORT || 3001;
app.listen(PORT, () => {
  console.log(`AI-Powered SaaS Platform #2 SaaS running on port ${PORT}`);
});
            