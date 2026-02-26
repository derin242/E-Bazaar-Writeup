# 🚩 E-Bazaar: ISSessions FantasyCTF 2026 Write-up
**Author:** Derin Ozturk  
**Role:** CTF Developer | 2nd Year Cyber Security Student, Sheridan College  
**Category:** Web Exploitation

---

## Background
The **E-Bazaar** was a spotlight challenge for the 2026 ISSessions FantasyCTF. Despite being my favorite challange out of all the challanges I've made, it remained unsolved by the end of the event. This write-up explores the three distinct web vulnerabilities required to "piece together" the 3-part flag.

![Challange Banner](https://github.com/user-attachments/assets/2182e93f-d2bf-4b1c-ad0f-a4db56c515c9)

### The Objective
Looking at the index page, the goal is to purchase items that seem unobtainable due to high prices or broken logic.

![Index Page](https://github.com/user-attachments/assets/0fee0c15-8c6f-4828-8bcb-fd4dc885946d)

The primary targets are the **Iced out magic wand** and the **Elixir vitae**.

![Target Items](https://github.com/user-attachments/assets/1d572564-9c92-42e9-9805-ff2a5610ebb9)

---

## 🕵️ Phase 1: Insecure Direct Object Reference (IDOR)
First, we check for hidden routes like `/admin`. While it exists, it is initially inaccessible.

![Admin Route Error](https://github.com/user-attachments/assets/1d1021a3-022c-430d-9fef-c59f8b8219e4)

By inspecting the index page source code, we find a hidden item with `item_id: 6`.

![Hidden Item Source](https://github.com/user-attachments/assets/3c85c146-0633-4684-8940-e77515f665a5)

**The Exploit:**
Using Burp Suite, we intercept the request responsible for adding an item to the cart.

![Original Add to Cart](https://github.com/user-attachments/assets/652ee213-843b-4f85-b46a-27ace523d21a)

We manually modify the `item_id` to `6` and set the `item_amount` to `1`.

![IDOR Modification](https://github.com/user-attachments/assets/1a18bd48-0a88-4f20-b1de-c9d74bc5edb7)

**Result:** The "Elixir of Invisibility" is successfully added. Checking out provides **Part 1 of the Flag**.

![Flag Part 1](https://github.com/user-attachments/assets/ab3d4d7f-4913-4ad6-980f-95eed3e0a45b)

---

## 💰 Phase 2: Negative Quantity & Logic Bypass
The **Iced Out Magic Wand** is too expensive. We can manipulate our balance by exploiting a lack of server-side validation on the `item_amount`.

**The Exploit:**
By sending a negative value for the amount, the total cost becomes negative, allowing us to gain money instead of losing it.

![Negative Amount Request](https://github.com/user-attachments/assets/835db283-31a9-443c-b825-c4c0fce31dca)

Attempting to checkout normally results in an error.

![Checkout Error](https://github.com/user-attachments/assets/83e02213-6a37-4ab1-a9bb-e9ba0267716b)

Intercepting the checkout request reveals parameters encoded in Ascii Hex and Base64: `cart_empty` and `force_checkout`.

![Checkout Parameters](https://github.com/user-attachments/assets/781dee22-6e60-4c19-a18b-acb24ee6f7c0)

We modify `force_checkout` to `True` (Base64: `VHJ1ZQ==`) and `cart_empty` to `False` (Base64: `RmFsc2U=`) to bypass the validation.

![Bypass Modification](https://github.com/user-attachments/assets/77f47f2b-dfc0-4c8b-9627-4aaaeb645a32)

**Result:** The error is bypassed. 

![Bypass Success](https://github.com/user-attachments/assets/bab2afff-1a47-43bc-a8e7-066bdf064bd8)

Our balance is now sufficient to purchase the "Iced Out Magic Wand".

![Massive Balance](https://github.com/user-attachments/assets/8cb2033c-5ed2-4e7a-baf9-2d11fcd7a85e)

Purchasing the wand grants **Part 2 of the Flag**.

![Flag Part 2](https://github.com/user-attachments/assets/1520dd88-2604-4011-9b8c-eb0d265f6dfe)

---

## 🍪 Phase 3: Cookie Manipulation & Admin Access
The final item, **Elixir Vitae**, has a price of `None`, breaking the cart system.
![Purchase Error (None Price)](https://github.com/user-attachments/assets/070db45b-c1f7-4910-ba46-a2ec9012c130)

**The Exploit:**
We can now visit the `/admin` route since we found the first 2 pieces.
Visiting the `/admin` route assigns an `auth` cookie.

![Admin Route](https://github.com/user-attachments/assets/a0481a5d-4d36-4556-8dc7-2acc8977d9f0)
![Auth Cookie](https://github.com/user-attachments/assets/0de9eb8c-3ebe-4db0-bd5b-d9fe566c8884)

The value of the cookie is `eyJ1c2VyIjogIk5vbmUiLCAibG9nZ2VkSW4iOiBmYWxzZX0=`. When decoded from Base64, it reveals a standard JSON object: `{"user": "None", "loggedIn": false}`.
To exploit this insecure session management, we first need to identify a valid username. Attempting to log in with random credentials returns a generic error message:

![Random Creds Error](https://github.com/user-attachments/assets/0998a65c-5b8f-4360-b58b-74c3dfff3e34)

However, when we try the username `admin`, the error message changes, confirming that the user `admin` exists but the password was incorrect. This is a classic "User Enumeration" vulnerability.

![Admin User Validation](https://github.com/user-attachments/assets/e1affa98-c29f-43e5-87ae-807ee752d0fe)

With the confirmed username, we can bypass the login logic entirely by spoofing the cookie.
We craft the new cookie: `{"user": "admin", "loggedIn": true}` (Base64: `eyJ1c2VyIjogImFkbWluIiwgImxvZ2dlZEluIjogdHJ1ZX0=`).

By refreshing the main page with our new credentials injected, we bypassed the login gate and gained full access to an administrative dashboard.

![Admin Panel](https://github.com/user-attachments/assets/5d60472e-d331-49e2-9a97-62d05695979a)

We change the price of the **Elixir Vitae** to a valid number.

![Price Change](https://github.com/user-attachments/assets/116a4df4-e73d-43c9-89fb-611583cb03f7)
![Price Updated Confirmation](https://github.com/user-attachments/assets/3873c327-0ef6-4be8-aa74-607c9bec0ab1)

Finally, we remove the admin cookie to return to the standard index page.

![Back to Shop](https://github.com/user-attachments/assets/e493b38e-2ce0-4778-8c4b-53522df66896)

**Final Step:** We add the Elixir to the cart and purchase it.

![Final Purchase](https://github.com/user-attachments/assets/2b2b05de-b298-48ac-8047-353cdb91350d)

**Result:** The final part of the flag is revealed, completing the challenge.

![Final Flag](https://github.com/user-attachments/assets/50e083eb-f067-43b9-9253-0a5f291f743e)

---

## 🛠️ Lessons Learned
* **Input Validation:** Never trust quantity or ID values sent from the client.
* **Secure Sessions:** Cookies should be signed or encrypted to prevent privilege escalation.
* **Business Logic:** Ensure checkout functions validate price states and enforce positive integers for quantities.

**Thanks for reading my write-up and I really hope you enjoyed!**
