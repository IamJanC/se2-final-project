document.addEventListener('DOMContentLoaded', function() {
    const cart = new Cart();
    
    // Get product ID from URL
    const urlParams = new URLSearchParams(window.location.search);
    const productId = urlParams.get('id');
    
    // In a real app, you would fetch the product details from an API
    // For now, we'll use a mock product
    const product = {
        id: productId,
        name: "Organic Free-Range Eggs",
        price: 12.99,
        image: "https://i.pinimg.com/474x/87/3f/2d/873f2dcf56d29f8db5f8fd3ed98b6477.jpg",
        description: "Our premium organic eggs come from happy, free-range chickens...",
        rating: 4.2
    };
    
    // Update product details on page
    document.querySelector('.product-title').textContent = product.name;
    document.querySelector('.price').textContent = `$${product.price.toFixed(2)}`;
    document.querySelector('.product-description').textContent = product.description;
    
    // Add to cart button
    document.querySelector('.add-to-cart').addEventListener('click', function() {
        const quantity = parseInt(document.getElementById('quantityInput').value);
        cart.addItem(product, quantity);
        alert(`${quantity} ${product.name} added to cart!`);
    });
    
    // Related products (simplified)
    const relatedProducts = [
        {id: '2', name: "Brown Eggs", price: 10.99, image: "https://i.pinimg.com/474x/6a/5f/4a/6a5f4a8e0fb8ef4a731f8b3ff70b656f.jpg"},
        {id: '3', name: "White Eggs", price: 11.99, image: "https://i.pinimg.com/474x/aa/23/44/aa23446987905e68b0c2140a35c5e7b9.jpg"}
    ];
    
    const relatedContainer = document.querySelector('.related-products .products-list');
    relatedProducts.forEach(product => {
        const card = document.createElement('div');
        card.className = 'product';
        card.innerHTML = `
            <a href="product.html?id=${product.id}">
                <img src="${product.image}" alt="${product.name}">
                <h3>${product.name}</h3>
            </a>
            <div class="price">$${product.price.toFixed(2)}</div>
            <button class="add-to-cart" data-id="${product.id}">Add to Cart</button>
        `;
        relatedContainer.appendChild(card);
    });
});