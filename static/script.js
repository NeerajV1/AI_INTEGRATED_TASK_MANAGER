async function submitJSON(api) { // Added async
    const userData = {
        username: document.getElementById('username').value,
        email: document.getElementById('email').value,
        password: document.getElementById('password').value,
        phoneno: document.getElementById('PhoneNo').value
    };

    const res = await fetch(api, {
        method: 'POST',
        headers: { // Fixed key name
            'Content-Type': 'application/json'
        },
        body: JSON.stringify(userData)
    });

    if (res.ok) {
        const html = await res.text(); // Use 'res' here
        document.open();
        document.write(html);
        document.close();
    } else {
        // Handle FastAPI HTTPExceptions
        const errorData = await res.json();
        alert("Login failed: " + errorData.detail);
    }
}
async function directSignUp(api){
    const res=await fetch(api);
    if(res.ok){
        const text=await res.text();
        document.open();
        document.write(text);
        document.close();
    }else{
        const errorData = await res.json();
        alert("Login failed: " + errorData.detail);
    }
}
async function logout(){
    await fetch("/logout",{
        method:'POST',
        credentials:"include"
    });
    window.location.href="/";
}