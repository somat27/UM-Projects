import { createSlice } from '@reduxjs/toolkit';

const initialState = {
  products: [], // Lista de produtos no carrinho
};

const orebiSlice = createSlice({
  name: 'orebi',
  initialState,
  reducers: {
    addToCart: (state, action) => {
      const itemIndex = state.products.findIndex(
        (item) => item._id === action.payload._id
      );
      if (itemIndex >= 0) {
        state.products[itemIndex].quantity += 1;
      } else {
        state.products.push({ ...action.payload, quantity: 1 });
      }
    },
    deleteItem: (state, action) => {
      state.products = state.products.filter(
        (item) => item._id !== action.payload
      );
    },
    increaseQuantity: (state, action) => {
      const itemIndex = state.products.findIndex(
        (item) => item._id === action.payload
      );
      if (itemIndex >= 0) {
        state.products[itemIndex].quantity += 1;
      }
    },
    drecreaseQuantity: (state, action) => {
      const itemIndex = state.products.findIndex(
        (item) => item._id === action.payload
      );
      if (itemIndex >= 0 && state.products[itemIndex].quantity > 1) {
        state.products[itemIndex].quantity -= 1;
      }
    },
    resetCart: (state) => {
      state.products = [];
    },
    // Nova função para atualizar a quantidade
    updateCartItemQuantity: (state, action) => {
      const { productId, quantity } = action.payload;
      const itemIndex = state.products.findIndex(
        (item) => item._id === productId
      );
      if (itemIndex >= 0) {
        state.products[itemIndex].quantity = quantity;
      }
    },
  },
});

export const {
  addToCart,
  deleteItem,
  increaseQuantity,
  drecreaseQuantity,
  resetCart,
  updateCartItemQuantity,
} = orebiSlice.actions;

export default orebiSlice.reducer;
