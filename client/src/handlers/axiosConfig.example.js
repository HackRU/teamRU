import Axios from "axios";

export const httpClient = Axios.create({
  baseURL: "",
  timeout: 5000
});
