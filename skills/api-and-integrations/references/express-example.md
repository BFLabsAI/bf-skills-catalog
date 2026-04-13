# Complete REST API Example: Express.js

Full working example showing pagination, validation, error handling, and standard response format.

```javascript
const express = require("express");
const app = express();

app.use(express.json());

// List users with pagination, filtering, and sorting
app.get("/api/v1/users", async (req, res) => {
  try {
    const page = parseInt(req.query.page) || 1;
    const limit = Math.min(parseInt(req.query.limit) || 20, 100);
    const offset = (page - 1) * limit;
    const { status, sort = "-createdAt" } = req.query;

    const where = {};
    if (status) where.status = status;

    const users = await User.findAndCountAll({
      where,
      limit,
      offset,
      order: parseSortParam(sort),
      attributes: ["id", "email", "firstName", "lastName", "createdAt"],
    });

    const totalPages = Math.ceil(users.count / limit);

    res.json({
      data: users.rows,
      meta: {
        total: users.count,
        page,
        perPage: limit,
        totalPages,
      },
      links: {
        self:  `/api/v1/users?page=${page}&limit=${limit}`,
        first: `/api/v1/users?page=1&limit=${limit}`,
        ...(page > 1         && { prev: `/api/v1/users?page=${page - 1}&limit=${limit}` }),
        ...(page < totalPages && { next: `/api/v1/users?page=${page + 1}&limit=${limit}` }),
        last: `/api/v1/users?page=${totalPages}&limit=${limit}`,
      },
    });
  } catch (error) {
    console.error("Error listing users:", error);
    res.status(500).json({
      error: { code: "INTERNAL_ERROR", message: "An error occurred while fetching users" },
    });
  }
});

// Get single user
app.get("/api/v1/users/:id", async (req, res) => {
  try {
    const user = await User.findByPk(req.params.id);
    if (!user) {
      return res.status(404).json({
        error: { code: "NOT_FOUND", message: "User not found" },
      });
    }
    res.json({ data: user });
  } catch (error) {
    res.status(500).json({
      error: { code: "INTERNAL_ERROR", message: "An error occurred" },
    });
  }
});

// Create user
app.post("/api/v1/users", async (req, res) => {
  try {
    const { email, firstName, lastName } = req.body;

    const validationErrors = [];
    if (!email)     validationErrors.push({ field: "email",     message: "Email is required" });
    if (!firstName) validationErrors.push({ field: "firstName", message: "First name is required" });
    if (!lastName)  validationErrors.push({ field: "lastName",  message: "Last name is required" });

    if (validationErrors.length > 0) {
      return res.status(422).json({
        error: {
          code: "VALIDATION_ERROR",
          message: "Missing required fields",
          details: validationErrors,
        },
      });
    }

    const user = await User.create({ email, firstName, lastName });
    res.status(201)
       .location(`/api/v1/users/${user.id}`)
       .json({ data: user });
  } catch (error) {
    if (error.name === "SequelizeUniqueConstraintError") {
      return res.status(409).json({
        error: { code: "CONFLICT", message: "Email already exists" },
      });
    }
    res.status(500).json({
      error: { code: "INTERNAL_ERROR", message: "An error occurred" },
    });
  }
});

// Partial update
app.patch("/api/v1/users/:id", async (req, res) => {
  try {
    const user = await User.findByPk(req.params.id);
    if (!user) {
      return res.status(404).json({
        error: { code: "NOT_FOUND", message: "User not found" },
      });
    }

    const allowed = ["firstName", "lastName", "email"];
    const updates = Object.fromEntries(
      Object.entries(req.body).filter(([k]) => allowed.includes(k))
    );

    await user.update(updates);
    res.json({ data: user });
  } catch (error) {
    res.status(500).json({
      error: { code: "INTERNAL_ERROR", message: "An error occurred" },
    });
  }
});

// Delete
app.delete("/api/v1/users/:id", async (req, res) => {
  try {
    const user = await User.findByPk(req.params.id);
    if (!user) {
      return res.status(404).json({
        error: { code: "NOT_FOUND", message: "User not found" },
      });
    }
    await user.destroy();
    res.status(204).send();
  } catch (error) {
    res.status(500).json({
      error: { code: "INTERNAL_ERROR", message: "An error occurred" },
    });
  }
});

// Helper: parse sort param like "-createdAt,firstName"
function parseSortParam(sort) {
  return sort.split(",").map((field) => {
    if (field.startsWith("-")) return [field.slice(1), "DESC"];
    return [field, "ASC"];
  });
}

app.listen(3000);
```
