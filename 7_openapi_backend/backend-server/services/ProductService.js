const Service = require('./Service');
const Product = require('../models/Product');

/**
* Lấy danh sách sản phẩm
*/
const productsGET = () => new Promise(
  async (resolve, reject) => {
    try {
      const items = await Product.find({});
      resolve(Service.successResponse(items));
    } catch (e) {
      reject(Service.rejectResponse(e.message || 'Invalid input', e.status || 500));
    }
  },
);

/**
* Xoá sản phẩm
*/
const productsIdDELETE = ({ id }) => new Promise(
  async (resolve, reject) => {
    try {
      const deleted = await Product.findByIdAndDelete(id);
      if (!deleted) {
        return reject(Service.rejectResponse('Sản phẩm không tồn tại', 404));
      }
      resolve(Service.successResponse(null, 204));
    } catch (e) {
      reject(Service.rejectResponse(e.message || 'Invalid ID', 500));
    }
  },
);

/**
* Lấy chi tiết sản phẩm
*/
const productsIdGET = ({ id }) => new Promise(
  async (resolve, reject) => {
    try {
      const item = await Product.findById(id);
      if (!item) {
        return reject(Service.rejectResponse('Sản phẩm không tồn tại', 404));
      }
      resolve(Service.successResponse(item));
    } catch (e) {
      reject(Service.rejectResponse(e.message || 'Invalid ID', 500));
    }
  },
);

/**
* Cập nhật sản phẩm
*/
const productsIdPUT = (args) => new Promise(
  async (resolve, reject) => {
    try {
      const id = args.id;
      const payload = args.productInput || args.body;
      const updated = await Product.findByIdAndUpdate(id, payload, { new: true });
      if (!updated) {
        return reject(Service.rejectResponse('Sản phẩm không tồn tại', 404));
      }
      resolve(Service.successResponse(updated));
    } catch (e) {
      reject(Service.rejectResponse(e.message || 'Invalid input', 500));
    }
  },
);

/**
* Tạo sản phẩm mới
*/
const productsPOST = (args) => new Promise(
  async (resolve, reject) => {
    try {
      const payload = args.productInput || args.body;
      const newItem = await Product.create(payload);
      resolve(Service.successResponse(newItem, 201));
    } catch (e) {
      reject(Service.rejectResponse(e.message || 'Invalid input', 422));
    }
  },
);

module.exports = {
  productsGET,
  productsIdDELETE,
  productsIdGET,
  productsIdPUT,
  productsPOST,
};
