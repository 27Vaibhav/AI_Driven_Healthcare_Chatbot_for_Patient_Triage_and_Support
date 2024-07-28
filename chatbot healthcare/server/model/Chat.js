const mongoose = require("mongoose");

const chatSchema = new mongoose.Schema({
  userMessage: { type: String, required: true },
  botMessage: { type: String, required: true },
  userId: { type: mongoose.Schema.Types.ObjectId, ref: "User", required: true },
  createdAt: { type: Date, default: Date.now },
});

const Chat = mongoose.model("Chat", chatSchema);

module.exports = Chat;
