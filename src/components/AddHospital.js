import { useState } from "react"
import { addHospital } from "../services/ApiService"

const AddHospital = ({ handleCancelBtn }) => {
    const [hospital, setHospital] = useState({
        name: '',
        address: '',
        phone: '',
        email: '',
        capacity: 0
    })

    const handleChange = (e) => {
        const { name, value } = e.target
        setHospital(prevHospital => ({
            ...prevHospital,
            [name]: value
        }))
    }

    const handleSubmit = (e) => {
        e.preventDefault()
        addHospital(hospital)
            .then(() => {
                handleCancelBtn()
            })
            .catch(error => {
                console.error('Error adding hospital:', error)
            })
    }

    return (
        <div className="container">
            <h3>Add New Hospital</h3>
            <form onSubmit={handleSubmit}>
                <div className="mb-3">
                    <label htmlFor="name" className="form-label">Hospital Name:</label>
                    <input
                        type="text"
                        className="form-control"
                        id="name"
                        name="name"
                        value={hospital.name}
                        onChange={handleChange}
                        required
                    />
                </div>
                <div className="mb-3">
                    <label htmlFor="address" className="form-label">Address:</label>
                    <textarea
                        className="form-control"
                        id="address"
                        name="address"
                        value={hospital.address}
                        onChange={handleChange}
                        rows="3"
                        required
                    />
                </div>
                <div className="mb-3">
                    <label htmlFor="phone" className="form-label">Phone:</label>
                    <input
                        type="tel"
                        className="form-control"
                        id="phone"
                        name="phone"
                        value={hospital.phone}
                        onChange={handleChange}
                        required
                    />
                </div>
                <div className="mb-3">
                    <label htmlFor="email" className="form-label">Email:</label>
                    <input
                        type="email"
                        className="form-control"
                        id="email"
                        name="email"
                        value={hospital.email}
                        onChange={handleChange}
                    />
                </div>
                <div className="mb-3">
                    <label htmlFor="capacity" className="form-label">Capacity:</label>
                    <input
                        type="number"
                        className="form-control"
                        id="capacity"
                        name="capacity"
                        value={hospital.capacity}
                        onChange={handleChange}
                        min="0"
                        required
                    />
                </div>
                <button type="submit" className="btn btn-primary">Add Hospital</button>
                <button type="button" className="btn btn-secondary ms-2" onClick={handleCancelBtn}>Cancel</button>
            </form>
        </div>
    )
}

export default AddHospital 