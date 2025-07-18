// server.js
const express = require('express');
const cors = require('cors');
const bodyParser = require('body-parser');
const mongoose = require('mongoose');
require('dotenv').config();

const app = express();
const PORT = process.env.PORT || 5000;

// Middleware
app.use(cors());
app.use(bodyParser.json());

// Root route
app.get('/', (req, res) => {
  res.redirect('/api');
});

// MongoDB Connection
mongoose.connect(process.env.MONGODB_URI || 'mongodb://localhost:27017/calendar-app', {
  useNewUrlParser: true,
  useUnifiedTopology: true
}).then(() => {
  console.log('Connected to MongoDB');
}).catch(err => {
  console.error('MongoDB connection error:', err);
});

// Log environment variables for debugging
console.log('Environment variables:');
console.log('BUG_SERVICE:', process.env.BUG_SERVICE);
console.log('CODE_REVIEW_SERVICE:', process.env.CODE_REVIEW_SERVICE);
console.log('FORUM_SERVICE:', process.env.FORUM_SERVICE);

// Event Schema
const eventSchema = new mongoose.Schema({
  title: { type: String, required: true },
  start: { type: Date, required: true },
  end: { type: Date, required: true },
  allDay: { type: Boolean, default: false },
  desc: { type: String },
  createdBy: { type: String },
  createdAt: { type: Date, default: Date.now },
  eventType: { type: String, enum: ['general', 'bug', 'code_review', 'forum_topic'], default: 'general' },
  referenceId: { type: String },
  status: { type: String },
  priority: { type: String, enum: ['low', 'medium', 'high'], default: 'medium' }
});

const Event = mongoose.model('Event', eventSchema);

// API Routes

const path = require('path');


app.get('/api', (req, res) => {
  res.send(`
    <!DOCTYPE html>
    <html>
      <head>
        <title>📅 Team Calendar API Docs</title>
        <style>
          body {
            font-family: 'Segoe UI', sans-serif;
            background: #f9f9f9;
            color: #333;
            padding: 40px;
            line-height: 1.6;
          }
          h1 {
            color: #2e86de;
            font-size: 2.2rem;
          }
          h2 {
            margin-top: 30px;
            color: #444;
          }
          .endpoint {
            background: #fff;
            padding: 15px;
            margin: 20px 0;
            border-left: 5px solid #2e86de;
            box-shadow: 0 0 8px rgba(0,0,0,0.05);
          }
          code {
            background: #f1f1f1;
            padding: 2px 6px;
            border-radius: 4px;
            font-family: monospace;
          }
          pre {
            background: #f4f4f4;
            padding: 10px;
            border-radius: 6px;
            overflow-x: auto;
            font-size: 14px;
          }
        </style>
      </head>
      <body>
        <h1>🎉 Team Calendar API</h1>
        <p>This backend powers the <strong>Team Calendar</strong> app, managing team events and schedules via a RESTful API.</p>

        <h2>📌 API Endpoints</h2>

        <div class="endpoint">
          <strong>GET</strong> <code>/api/events</code><br/>
          <p>Get all events.</p>
          <strong>Response:</strong>
          <pre>[
  {
    "_id": "abc123",
    "title": "Team Meeting",
    "start": "2025-04-10T10:00:00.000Z",
    "end": "2025-04-10T11:00:00.000Z",
    "desc": "Discuss roadmap",
    "allDay": false,
    "createdBy": "musadiq"
  }
]</pre>
        </div>

        <div class="endpoint">
          <strong>GET</strong> <code>/api/events/:id</code><br/>
          <p>Get a single event by ID.</p>
          <strong>Example:</strong> <code>/api/events/abc123</code><br/>
          <strong>Response:</strong>
          <pre>{
  "_id": "abc123",
  "title": "Team Meeting",
  "start": "2025-04-10T10:00:00.000Z",
  "end": "2025-04-10T11:00:00.000Z",
  "desc": "Discuss roadmap",
  "createdBy": "musadiq"
}</pre>
        </div>

        <div class="endpoint">
          <strong>GET</strong> <code>/api/events/createdBy/:user</code><br/>
          <p>Get all events created by a specific user.</p>
          <strong>Example:</strong> <code>/api/events/createdBy/musadiq</code><br/>
          <strong>Response:</strong>
          <pre>[
  {
    "title": "Demo Day",
    "start": "2025-04-12T14:00:00.000Z",
    "end": "2025-04-12T16:00:00.000Z",
    "desc": "Final presentation",
    "createdBy": "musadiq"
  }
]</pre>
        </div>

        <div class="endpoint">
          <strong>POST</strong> <code>/api/events</code><br/>
          <p>Create a new event.</p>
          <strong>Sample Request Body:</strong>
          <pre>{
  "title": "Hackathon",
  "start": "2025-04-15T09:00:00Z",
  "end": "2025-04-15T17:00:00Z",
  "desc": "Build cool stuff",
  "allDay": false,
  "createdBy": "govu"
}</pre>
          <strong>Sample Response:</strong>
          <pre>{
  "_id": "xyz789",
  "title": "Hackathon",
  "start": "2025-04-15T09:00:00Z",
  "end": "2025-04-15T17:00:00Z",
  "desc": "Build cool stuff",
  "createdBy": "govu"
}</pre>
        </div>

        <div class="endpoint">
          <strong>PUT</strong> <code>/api/events/:id</code><br/>
          <p>Update an existing event by ID.</p>
          <strong>Example:</strong> <code>/api/events/abc123</code><br/>
          <strong>Sample Body:</strong>
          <pre>{
  "title": "Updated Title"
}</pre>
          <strong>Response:</strong>
          <pre>{
  "_id": "abc123",
  "title": "Updated Title"
}</pre>
        </div>

        <div class="endpoint">
          <strong>DELETE</strong> <code>/api/events/:id</code><br/>
          <p>Delete an event by ID.</p>
          <strong>Example:</strong> <code>/api/events/abc123</code><br/>
          <strong>Response:</strong>
          <pre>{ "message": "Event deleted successfully" }</pre>
        </div>

        <div class="endpoint">
          <strong>GET</strong> <code>/api/events/range?start=2025-04-01&end=2025-04-30</code><br/>
          <p>Get events between specific dates.</p>
          <strong>Response:</strong>
          <pre>[
  {
    "title": "Demo Day",
    "start": "2025-04-12T14:00:00.000Z",
    "end": "2025-04-12T16:00:00.000Z"
  }
]</pre>
        </div>

        <div class="endpoint">
          <strong>GET</strong> <code>/api/events/upcoming</code><br/>
          <p>Get all future events from now.</p>
          <strong>Response:</strong>
          <pre>[
  {
    "title": "Presentation",
    "start": "2025-04-22T12:00:00Z",
    "end": "2025-04-22T13:00:00Z"
  }
]</pre>
        </div>

        <div class="endpoint">
          <strong>GET</strong> <code>/api/events/search/:query</code><br/>
          <p>Search events by title or description.</p>
          <strong>Example:</strong> <code>/api/events/search/hack</code><br/>
          <strong>Response:</strong>
          <pre>[
  {
    "title": "Hackathon",
    "desc": "Build cool stuff"
  }
]</pre>
        </div>

        <h2>🛠 Tech Stack</h2>
        <ul>
          <li>Node.js + Express</li>
          <li>MongoDB (Mongoose)</li>
          <li>React frontend (separate client)</li>
        </ul>

        <p style="margin-top: 40px;">Made with ❤ by <strong>Musadiq</strong> & <strong>Govu</strong></p>
      </body>
    </html>
  `);
});


// Get all events admin
app.get('/api/events', async (req, res) => {
  try {
    const events = await Event.find();
    res.json(events);
  } catch (err) {
    res.status(500).json({ message: err.message });
  }
});



// Get events by createdBy
app.get('/api/events/createdBy/:user', async (req, res) => {
  try {
    const events = await Event.find({ createdBy: req.params.user });
    if (!events || events.length === 0) {
      return res.status(404).json({ message: 'No events found for this user' });
    }
    res.json(events);
  } catch (err) {
    res.status(500).json({ message: err.message });
  }
});


// Create a new event
app.post('/api/events', async (req, res) => {
  try {
    const event = new Event(req.body);
    const savedEvent = await event.save();
    res.status(201).json(savedEvent);
  } catch (err) {
    res.status(400).json({ message: err.message });
  }
});



// 1. Search Events by Title (Partial Match) admin
app.get('/api/events/search/:query', async (req, res) => {
  try {
    const regex = new RegExp(req.params.query, 'i'); // case-insensitive
    const results = await Event.find({ title: { $regex: regex } });
    res.json(results);
  } catch (err) {
    res.status(500).json({ message: err.message });
  }
});

// users
app.get('/api/events/search/:username/:query', async (req, res) => {
  try {
    const { username, query } = req.params;
    const regex = new RegExp(query, 'i'); // case-insensitive

    const results = await Event.find({
      createdBy: username,
      title: { $regex: regex }
    });

    res.json(results);
  } catch (err) {
    res.status(500).json({ message: err.message });
  }
});


// Filter Events by Date Range
app.get('/api/events/range', async (req, res) => {
  try {
    const { start, end } = req.query;
    const events = await Event.find({
      start: { $gte: new Date(start) },
      end: { $lte: new Date(end) }
    });
    res.json(events);
  } catch (err) {
    res.status(500).json({ message: err.message });
  }
});

// gte all ucpoming evenrts admin

app.get('/api/events/upcoming', async (req, res) => {
  try {
    const today = new Date();
    const events = await Event.find({ start: { $gte: today } }).sort({ start: 1 });
    res.json(events);
  } catch (err) {
    res.status(500).json({ message: err.message });
  }
});



app.get('/api/events/upcoming/:username', async (req, res) => {
  try {
    const { username } = req.params;
    const today = new Date();

    const events = await Event.find({
      createdBy: username,
      start: { $gte: today }
    }).sort({ start: 1 });

    res.json(events);
  } catch (err) {
    res.status(500).json({ message: err.message });
  }
});


// unique users names admin

app.get('/api/users', async (req, res) => {
  try {
    const users = await Event.distinct('createdBy');
    res.json(users);
  } catch (err) {
    res.status(500).json({ message: err.message });
  }
});

// evnrts per user

app.get('/api/stats/events-per-user', async (req, res) => {
  try {
    const stats = await Event.aggregate([
      { $group: { _id: '$createdBy', count: { $sum: 1 } } },
      { $sort: { count: -1 } }
    ]);
    res.json(stats);
  } catch (err) {
    res.status(500).json({ message: err.message });
  }
});


// Get event by ID
app.get('/api/events/:id', async (req, res) => {
  try {
    const event = await Event.findById(req.params.id);
    if (!event) {
      return res.status(404).json({ message: 'Event not found' });
    }
    res.json(event);
  } catch (err) {
    res.status(500).json({ message: err.message });
  }
});

// Update an event
app.put('/api/events/:id', async (req, res) => {
  try {
    const updatedEvent = await Event.findByIdAndUpdate(
      req.params.id,
      req.body,
      { new: true }
    );
    if (!updatedEvent) {
      return res.status(404).json({ message: 'Event not found' });
    }
    res.json(updatedEvent);
  } catch (err) {
    res.status(400).json({ message: err.message });
  }
});

// Delete an event
app.delete('/api/events/:id', async (req, res) => {
  try {
    const deletedEvent = await Event.findByIdAndDelete(req.params.id);
    if (!deletedEvent) {
      return res.status(404).json({ message: 'Event not found' });
    }
    res.json({ message: 'Event deleted successfully' });
  } catch (err) {
    res.status(500).json({ message: err.message });
  }
});

// Add new endpoint to create events from bugs
app.post('/api/events/bug', async (req, res) => {
  try {
    const { bug_id, title, description, status, createdBy } = req.body;

    // Set end date to 3 days from now as a default deadline
    const startDate = new Date();
    const endDate = new Date();
    endDate.setDate(endDate.getDate() + 3);

    const event = new Event({
      title: `Bug: ${title}`,
      start: startDate,
      end: endDate,
      desc: description || 'No description provided',
      eventType: 'bug',
      referenceId: bug_id,
      status: status || 'Pending',
      createdBy: createdBy || 'system'
    });

    const savedEvent = await event.save();
    console.log(`Created calendar event for bug ${bug_id}:`, savedEvent);
    res.status(201).json(savedEvent);
  } catch (err) {
    console.error('Error creating bug event:', err);
    res.status(400).json({ message: err.message });
  }
});

// Add new endpoint to create events from code reviews
app.post('/api/events/code-review', async (req, res) => {
  try {
    const { review_id, title, description, status, createdBy, reviewer_id } = req.body;

    // Set end date to 2 days from now as a default deadline for code reviews
    const startDate = new Date();
    const endDate = new Date();
    endDate.setDate(endDate.getDate() + 2);

    const event = new Event({
      title: `Review: ${title}`,
      start: startDate,
      end: endDate,
      desc: description || 'No description provided',
      eventType: 'code_review',
      referenceId: review_id,
      status: status || 'Pending',
      createdBy: createdBy || 'system'
    });

    const savedEvent = await event.save();
    console.log(`Created calendar event for code review ${review_id}:`, savedEvent);
    res.status(201).json(savedEvent);
  } catch (err) {
    console.error('Error creating code review event:', err);
    res.status(400).json({ message: err.message });
  }
});

// Add endpoint to fetch all bug-related events
app.get('/api/events/bugs', async (req, res) => {
  try {
    const events = await Event.find({ eventType: 'bug' });
    res.json(events);
  } catch (err) {
    res.status(500).json({ message: err.message });
  }
});

// Add endpoint to create events from forum topics
app.post('/api/events/forum-topic', async (req, res) => {
  try {
    console.log('Received request to create forum topic event');
    console.log('Request body:', req.body);

    const { title, description, start, end, referenceId, status, createdBy } = req.body;

    // Handle date parsing more carefully
    let startDate, endDate;
    try {
      startDate = start ? new Date(start) : new Date();
      if (isNaN(startDate.getTime())) {
        console.log('Invalid start date, using current time');
        startDate = new Date();
      }
    } catch (e) {
      console.log('Error parsing start date:', e);
      startDate = new Date();
    }

    try {
      endDate = end ? new Date(end) : new Date(new Date().getTime() + 24 * 60 * 60 * 1000);
      if (isNaN(endDate.getTime())) {
        console.log('Invalid end date, using default (1 day later)');
        endDate = new Date(new Date().getTime() + 24 * 60 * 60 * 1000);
      }
    } catch (e) {
      console.log('Error parsing end date:', e);
      endDate = new Date(new Date().getTime() + 24 * 60 * 60 * 1000);
    }

    // Create event for forum topic
    const event = new Event({
      title: title || 'Forum Topic',
      start: startDate,
      end: endDate,
      desc: description || 'No description provided',
      eventType: 'forum_topic',
      referenceId: referenceId,
      status: status || 'active',
      createdBy: createdBy || 'forum_service'
    });

    console.log('Creating event with data:', {
      title: event.title,
      start: event.start,
      end: event.end,
      desc: event.desc,
      eventType: event.eventType,
      referenceId: event.referenceId
    });

    const savedEvent = await event.save();
    console.log(`Created calendar event for forum topic ${referenceId}:`, savedEvent);
    res.status(201).json(savedEvent);
  } catch (err) {
    console.error('Error creating forum topic event:', err);
    res.status(400).json({ message: err.message });
  }
});

// Add endpoint to fetch all forum topic events
app.get('/api/events/forum-topics', async (req, res) => {
  try {
    const events = await Event.find({ eventType: 'forum_topic' });
    res.json(events);
  } catch (err) {
    res.status(500).json({ message: err.message });
  }
});

// Get events by reference ID
app.get('/api/events/by-reference/:referenceId', async (req, res) => {
  try {
    const { referenceId } = req.params;
    const event = await Event.findOne({ referenceId });

    if (!event) {
      return res.status(404).json({ message: 'Event not found' });
    }

    res.json(event);
  } catch (err) {
    res.status(500).json({ message: err.message });
  }
});

// Update event by reference ID
app.put('/api/events/by-reference/:referenceId', async (req, res) => {
  try {
    const { referenceId } = req.params;
    const updatedEvent = await Event.findOneAndUpdate(
      { referenceId },
      req.body,
      { new: true }
    );

    if (!updatedEvent) {
      return res.status(404).json({ message: 'Event not found' });
    }

    res.json(updatedEvent);
  } catch (err) {
    res.status(400).json({ message: err.message });
  }
});

// Add endpoint to fetch all code review-related events
app.get('/api/events/code-reviews', async (req, res) => {
  try {
    const events = await Event.find({ eventType: 'code_review' });
    res.json(events);
  } catch (err) {
    res.status(500).json({ message: err.message });
  }
});

// Delete event by reference ID
app.delete('/api/events/by-reference/:referenceId', async (req, res) => {
  try {
    console.log(`Received request to delete event with referenceId: ${req.params.referenceId}`);

    const { referenceId } = req.params;
    const result = await Event.findOneAndDelete({ referenceId });

    if (!result) {
      console.log(`No event found with referenceId: ${referenceId}`);
      return res.status(404).json({ message: 'Event not found' });
    }

    console.log(`Successfully deleted event with referenceId: ${referenceId}`);
    res.json({ message: 'Event deleted successfully', deletedEvent: result });
  } catch (err) {
    console.error('Error deleting event:', err);
    res.status(500).json({ message: err.message });
  }
});



// Start the server
app.listen(PORT, '0.0.0.0', () => {
  console.log(`Server is live on 0.0.0.0:${PORT}`);
});
