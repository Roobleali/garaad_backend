const express = require("express");
const cors = require("cors");
const helmet = require("helmet");
const morgan = require("morgan");
const mongoose = require("mongoose");
const rateLimit = require("express-rate-limit");
require("dotenv").config();

// Import routes
const authRoutes = require("./routes/auth.routes");
const userRoutes = require("./routes/user.routes");
const leagueRoutes = require("./routes/league.routes");
const gamificationRoutes = require("./routes/gamification.routes");
const notificationRoutes = require("./routes/notification.routes");
const courseRoutes = require("./routes/course.routes");
const lessonRoutes = require("./routes/lesson.routes");
const problemRoutes = require("./routes/problem.routes");

// Import middleware
const { errorHandler } = require("./middleware/error.middleware");
const { authMiddleware } = require("./middleware/auth.middleware");

const app = express();

// Security middleware
app.use(helmet());
app.use(cors());
app.use(express.json());
app.use(express.urlencoded({ extended: true }));
app.use(morgan("dev"));

// Rate limiting
const limiter = rateLimit({
  windowMs: 15 * 60 * 1000, // 15 minutes
  max: 100, // limit each IP to 100 requests per windowMs
});
app.use(limiter);

// Health check endpoint
app.get("/health", (req, res) => {
  res.json({
    status: "healthy",
    version: "1.0.0",
    database:
      mongoose.connection.readyState === 1 ? "connected" : "disconnected",
  });
});

app.get("/", (req, res) => {
  res.json({
    message: "Garaad Express API",
    version: "1.0.0",
  });
});

// Routes
app.use("/api/auth", authRoutes);
app.use("/api/users", authMiddleware, userRoutes);
// Match Django URL structure
app.use("/api/league/leagues", authMiddleware, leagueRoutes);
app.use("/api/gamification", authMiddleware, gamificationRoutes);
app.use("/api/lms/notifications", authMiddleware, notificationRoutes);
app.use("/api/lms/courses", authMiddleware, courseRoutes);
app.use("/api/lms/lessons", authMiddleware, lessonRoutes);
app.use("/api/lms/problems", authMiddleware, problemRoutes);

// Legacy routes for backward compatibility
app.use("/api/league", authMiddleware, leagueRoutes);
app.use("/api/notifications", authMiddleware, notificationRoutes);
app.use("/api/courses", authMiddleware, courseRoutes);
app.use("/api/lessons", authMiddleware, lessonRoutes);
app.use("/api/problems", authMiddleware, problemRoutes);

// Error handling
app.use(errorHandler);

// Database connection
const MONGODB_URI =
  process.env.MONGODB_URI || "mongodb://localhost:27017/garaad";
mongoose
  .connect(MONGODB_URI)
  .then(() => console.log("Connected to MongoDB"))
  .catch((err) => console.error("MongoDB connection error:", err));

// Export app
module.exports = app;
