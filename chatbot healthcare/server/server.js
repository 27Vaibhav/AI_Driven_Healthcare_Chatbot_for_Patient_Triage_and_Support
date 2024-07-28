const express = require("express");
const mongoose = require("mongoose");
const bcrypt = require("bcryptjs");
const jwt = require("jsonwebtoken");
const cookieParser = require("cookie-parser");
const cors = require("cors");
const User = require("./model/User");
const Chat = require("./model/Chat");
const app = express();

mongoose
  .connect(
    "mongodb+srv://yadvendrashukla919:D5JEpdLJfCV2cGW8@cluster0.jy1uwsf.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0",
    {
      useNewUrlParser: true,
      useUnifiedTopology: true,
    }
  )
  .then(() => console.log("Connected to MongoDB"))
  .catch((err) => console.error("Failed to connect to MongoDB", err));

app.use(express.json());
app.use(cookieParser());
app.use(cors({ origin: "http://localhost:3000", credentials: true }));

const authMiddleware = (req, res, next) => {
  const token = req.cookies.token;
  if (!token) return res.sendStatus(401);

  jwt.verify(token, "secret", (err, user) => {
    if (err) return res.sendStatus(403);
    req.user = user;
    next();
  });
};

app.post("/api/register", async (req, res) => {
  const { name, gender, email, password } = req.body;
  const hashedPassword = await bcrypt.hash(password, 10);
  const user = new User({ name, gender, email, password: hashedPassword });
  await user.save();
  res.sendStatus(201);
});

app.post("/api/login", async (req, res) => {
  const { email, password } = req.body;
  const user = await User.findOne({ email });
  if (!user) return res.sendStatus(401);
  const isMatch = await bcrypt.compare(password, user.password);
  if (!isMatch) return res.sendStatus(401);

  const token = jwt.sign(
    { id: user._id, email: user.email, name: user.name, gender: user.gender },
    "secret",
    { expiresIn: "1h" }
  );
  res.cookie("token", token, { httpOnly: true }).sendStatus(200);
});

app.get("/api/me", authMiddleware, (req, res) => {
  res.json(req.user);
});

app.post("/api/logout", (req, res) => {
  res.clearCookie("token").sendStatus(200);
});

// Endpoint to save chat history
app.post("/api/chat", authMiddleware, async (req, res) => {
  const { userMessage, botMessage, userId } = req.body;
  const chat = new Chat({ userMessage, botMessage, userId });
  await chat.save();
  res.sendStatus(201);
});

app.listen(8000, () => {
  console.log("Server is running on port 8000");
});
