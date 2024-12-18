var updateBtns = document.getElementsByClassName('update-cart')
for (i = 0; i < updateBtns.length; i++) {
    updateBtns[i].addEventListener('click', function () {
        var productId = this.dataset.product
        var action = this.dataset.action
        console.log('productId', productId, 'action', action)
        console.log('user:', user)
        if (user === "AnonymousUser") {
            console.log('user is not logged in')
        } else {
            updateUserOder(productId, action)
        }
    })
}
function updateUserOder(productId, action) {
    console.log('user is logged in, success add')
    var url = '/update_item/'
    fetch(url, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': csrftoken,
        },
        body: JSON.stringify({ 'productId': productId, 'action': action })
    })
        // .then((response) => {
        //     return response.json()
        // })
        .then((response) => response.json())
        .then((data) => {

            location.reload()


        })
}

