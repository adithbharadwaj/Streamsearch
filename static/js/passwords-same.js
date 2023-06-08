function passwordsSame() {
    console.log("Called passwordsSame!");
    password = document.getElementsByName("password")[0];
    password_confirm = document.getElementsByName("password_confirm")[0];

    password_confirm.setCustomValidity(
        password_confirm.value != password.value ? "Passwords do not match." : ""
    );
}
