const signupForm = document.querySelector("#registerForm");
const loginForm = document.querySelector("#loginForm");
const editBookForm = document.querySelector("#editForm");
const deleteBtn = document.querySelector("#deleteBtn");


function getCookie(name) {
    let cookieValue = null;

    if (document.cookie && document.cookie !== '') {
        const allCookies = document.cookie.split(';');
        for (const cookie of allCookies) {
            const eqPos = cookie.indexOf('=') > -1 ? cookie.indexOf('=') : null;
            cookieValue = eqPos ? cookie.substring(eqPos+1) : null;
        }
    }

    return cookieValue;
}


if (signupForm) {
    signupForm.addEventListener("submit", async event => {
        event.preventDefault();

        const form = event.target;
        const formData = new FormData(form);

        const data = Object.fromEntries(formData.entries());

        const payload = {
            username: data.username,
            email: data.email,
            password: data.password,
            role: data.role
        }

        try {
            const response = await fetch('/auth/register', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(payload)
            });
            if (response.ok) {
                window.location.href = '/auth/login-page';
            } else {
                const respJSON = await response.json();
                const errorData = respJSON.detail;
                alert(`Error, ${errorData}`);
            }
        } catch (err) {
            console.error('Request failed:', err);
            alert('An error happened. Please try again.');
        }
    })
}


if (loginForm) {
    loginForm.addEventListener("submit", async event => {
        event.preventDefault();

        const form = event.target;
        const formData = new FormData(form);

        // const data = Object.fromEntries(formData.entries());

        // const payload = {
        //     username: data.username,
        //     email: data.email,
        //     password: data.password
        // }

        const payload = new URLSearchParams();

        for (const [key, value] of formData.entries()) {
            payload.append(key, value);
        }

        try {
            const response = await fetch('/auth/token', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/x-www-form-urlencoded'
                },
                body: payload.toString()
            });
            if (response.ok) {
                const respJson = await response.json();
                token = respJson.access_token;
                document.cookie = `access_token=${token};path=/`;
                window.location.href = '/books/my-books-page';
            } else {
                const respJSON = await response.json();
                const errorData = respJSON.detail;
                alert(`Error, ${errorData}`);
            }
        } catch (err) {
            alert('An error happened. Please try again.');
        }


    })
}


if (editBookForm) {
    editBookForm.addEventListener("submit", async event => {

        event.preventDefault();

        const currentLink = window.location.href;
        const book_id = currentLink.split('/').splice(-1)[0].split('?')[0];

        const form = event.target;
        const formData = new FormData(form);

        data = Object.fromEntries(formData.entries());

        const payload = {
            title: data.title,
            author: data.author,
            summary: data.summary,
            category: data.category
        }

        try {
            const token = getCookie('access_token');
            const response = await fetch(`/books/edit-book/${book_id}`, {
                method: 'PUT',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${token}`
                },
                body: JSON.stringify(payload)
            });

            if (response.ok) {
                window.location.href = '/books/my-books-page';
            } else {
                const errorData = await response.json();
                alert(`Error, ${errorData}`);
            }
        } catch (error) {
            console.error('Error:', error);
            alert('An error occured. Please try again.');
        }
    });
}


if (deleteBtn) {
    deleteBtn.addEventListener("click", async event => {
        const url = window.location.pathname;
        const book_id = Number(url.substring(url.lastIndexOf('/') + 1));

        const token = getCookie('access_token');
        
        const response = await fetch(`/books/delete-book/${book_id}`, {
            method: 'DELETE',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${token}`
            }
        });
        
        try {
            if (response.ok) {
                window.location.href = '/books/my-books-page';
            } else {
                const respJSON = await response.json();
                const errorData = respJSON.detail;
                alert(`Error, ${errorData}`);
            }
        }
        catch(error) {
            console.error(error);
            alert ('Something happened, try again!');
        }
    });
}