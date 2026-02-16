import React, { useEffect, useState } from "react";
import axios from "axios";

function Dashboard() {
  const [expenses, setExpenses] = useState([]);
  const [title, setTitle] = useState("");
  const [amount, setAmount] = useState("");
  const [category, setCategory] = useState("");
  const [date, setDate] = useState("");
  const [budget, setBudget] = useState("");
  const [currentBudget, setCurrentBudget] = useState(0);

  const user_id = localStorage.getItem("user_id");

  const fetchExpenses = async () => {
    const res = await axios.get(
      `http://127.0.0.1:5000/get_expenses/${user_id}`
    );
    setExpenses(res.data);
  };

  const fetchBudget = async () => {
    const res = await axios.get(
      `http://127.0.0.1:5000/get_budget/${user_id}`
    );
    setCurrentBudget(res.data.budget);
  };

  useEffect(() => {
    fetchExpenses();
    fetchBudget();
  }, []);

  const addExpense = async () => {
    await axios.post("http://127.0.0.1:5000/add_expense", {
      title,
      amount,
      category,
      date,
      user_id,
    });
    fetchExpenses();
  };

  const deleteExpense = async (id) => {
    await axios.delete(
      `http://127.0.0.1:5000/delete_expense/${id}`
    );
    fetchExpenses();
  };

  const totalExpense = expenses.reduce(
    (sum, exp) => sum + Number(exp.amount),
    0
  );

  const setUserBudget = async () => {
    await axios.post("http://127.0.0.1:5000/set_budget", {
      amount: budget,
      user_id,
    });
    fetchBudget();
  };

  return (
    <div className="dashboard">
      <h2>Expense Dashboard</h2>

      <h3>Total Expense: ₹{totalExpense}</h3>
      <h3>Budget: ₹{currentBudget}</h3>

      {totalExpense > currentBudget && currentBudget !== 0 && (
        <p style={{ color: "red" }}>⚠ Budget Exceeded!</p>
      )}

      <div className="add-expense">
        <input placeholder="Title" onChange={(e) => setTitle(e.target.value)} />
        <input placeholder="Amount" onChange={(e) => setAmount(e.target.value)} />
        <input placeholder="Category" onChange={(e) => setCategory(e.target.value)} />
        <input type="date" onChange={(e) => setDate(e.target.value)} />
        <button onClick={addExpense}>Add Expense</button>
      </div>

      <div className="add-expense">
        <input
          placeholder="Set Budget"
          onChange={(e) => setBudget(e.target.value)}
        />
        <button onClick={setUserBudget}>Save Budget</button>
      </div>

      <ul>
        {expenses.map((exp) => (
          <li key={exp.id}>
            {exp.title} - ₹{exp.amount} ({exp.category})
            <button
              onClick={() => deleteExpense(exp.id)}
              style={{ marginLeft: "10px" }}
            >
              Delete
            </button>
          </li>
        ))}
      </ul>

      <button
        onClick={() => {
          localStorage.removeItem("user_id");
          window.location.href = "/";
        }}
      >
        Logout
      </button>
    </div>
  );
}

export default Dashboard;
