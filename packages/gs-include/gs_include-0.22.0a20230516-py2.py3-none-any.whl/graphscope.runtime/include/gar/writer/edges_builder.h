/** Copyright 2022 Alibaba Group Holding Limited.

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
*/

#ifndef GAR_WRITER_EDGES_BUILDER_H_
#define GAR_WRITER_EDGES_BUILDER_H_

#include <algorithm>
#include <any>
#include <memory>
#include <string>
#include <unordered_map>
#include <vector>

#include "gar/writer/arrow_chunk_writer.h"

namespace GAR_NAMESPACE_INTERNAL {
namespace builder {

/**
 * @brief Edge is designed for constructing edges builder.
 *
 */
class Edge {
 public:
  /**
   * @brief Initialize the edge with its source and destination.
   *
   * @param src_id The id of the source vertex.
   * @param dst_id The id of the destination vertex.
   */
  explicit Edge(IdType src_id, IdType dst_id)
      : src_id_(src_id), dst_id_(dst_id), empty_(true) {}

  /**
   * @brief Check if the edge is empty.
   *
   * @return true/false.
   */
  inline bool Empty() const noexcept { return empty_; }

  /**
   * @brief Get source id of the edge.
   *
   * @return The id of the source vertex.
   */
  inline IdType GetSource() const noexcept { return src_id_; }

  /**
   * @brief Get destination id of the edge.
   *
   * @return The id of the destination vertex.
   */
  inline IdType GetDestination() const noexcept { return dst_id_; }

  /**
   * @brief Add a property to the edge.
   *
   * @param name The name of the property.
   * @param val The value of the property.
   */
  inline void AddProperty(const std::string& name, const std::any& val) {
    empty_ = false;
    properties_[name] = val;
  }

  /**
   * @brief Get a property of the edge.
   *
   * @param property The name of the property.
   * @return The value of the property.
   */
  inline const std::any& GetProperty(const std::string& property) const {
    return properties_.at(property);
  }

  /**
   * @brief Get all properties of the edge.
   *
   * @return The map containing all properties of the edge.
   */
  inline const std::unordered_map<std::string, std::any>& GetProperties()
      const {
    return properties_;
  }

  /**
   * @brief Check if the edge contains a property.
   *
   * @param property The name of the property.
   * @return true/false.
   */
  inline bool ContainProperty(const std::string& property) const {
    return (properties_.find(property) != properties_.end());
  }

 private:
  IdType src_id_, dst_id_;
  bool empty_;
  std::unordered_map<std::string, std::any> properties_;
};

/**
 * @brief The compare function for sorting edges by source id.
 *
 * @param a The first edge to compare.
 * @param b The second edge to compare.
 * @return If a is less than b: true/false.
 */
inline bool cmp_src(const Edge& a, const Edge& b) {
  return a.GetSource() < b.GetSource();
}

/**
 * @brief The compare function for sorting edges by destination id.
 *
 * @param a The first edge to compare.
 * @param b The second edge to compare.
 * @return If a is less than b: true/false.
 */
inline bool cmp_dst(const Edge& a, const Edge& b) {
  return a.GetDestination() < b.GetDestination();
}

/**
 * @brief EdgeBuilder is designed for building and writing a collection of
 * edges.
 *
 */
class EdgesBuilder {
 public:
  /**
   * @brief Initialize the EdgesBuilder.
   *
   * @param edge_info The edge info that describes the vertex type.
   * @param prefix The absolute prefix.
   * @param adj_list_type The adj list type of the edges.
   * @param num_vertices The total number of vertices for source or destination.
   */
  explicit EdgesBuilder(const EdgeInfo edge_info, const std::string& prefix,
                        AdjListType adj_list_type, IdType num_vertices)
      : edge_info_(edge_info),
        prefix_(prefix),
        adj_list_type_(adj_list_type),
        num_vertices_(num_vertices) {
    edges_.clear();
    num_edges_ = 0;
    is_saved_ = false;
    switch (adj_list_type) {
    case AdjListType::unordered_by_source:
      vertex_chunk_size_ = edge_info_.GetSrcChunkSize();
      break;
    case AdjListType::ordered_by_source:
      vertex_chunk_size_ = edge_info_.GetSrcChunkSize();
      break;
    case AdjListType::unordered_by_dest:
      vertex_chunk_size_ = edge_info_.GetDstChunkSize();
      break;
    case AdjListType::ordered_by_dest:
      vertex_chunk_size_ = edge_info_.GetDstChunkSize();
      break;
    default:
      vertex_chunk_size_ = edge_info_.GetSrcChunkSize();
    }
  }

  /**
   * @brief Check if adding an edge is allowed.
   *
   * @param e The edge to add.
   * @return Status: ok or status::InvalidOperation error.
   */
  Status Validate(const Edge& e) {
    // can not add new edges
    if (is_saved_) {
      return Status::InvalidOperation("can not add new edges after dumping");
    }
    // invalid adj list type
    if (!edge_info_.ContainAdjList(adj_list_type_)) {
      return Status::InvalidOperation("invalid adj list type");
    }
    // contain invalid properties
    for (auto& property : e.GetProperties()) {
      if (!edge_info_.ContainProperty(property.first))
        return Status::InvalidOperation("invalid property");
    }
    return Status::OK();
  }

  /**
   * @brief Get the vertex chunk index of a given edge.
   *
   * @param e The edge to add.
   * @return The vertex chunk index of the edge.
   */
  IdType getVertexChunkIndex(const Edge& e) {
    switch (adj_list_type_) {
    case AdjListType::unordered_by_source:
      return e.GetSource() / vertex_chunk_size_;
    case AdjListType::ordered_by_source:
      return e.GetSource() / vertex_chunk_size_;
    case AdjListType::unordered_by_dest:
      return e.GetDestination() / vertex_chunk_size_;
    case AdjListType::ordered_by_dest:
      return e.GetDestination() / vertex_chunk_size_;
    default:
      return e.GetSource() / vertex_chunk_size_;
    }
  }

  /**
   * @brief Add an edge to the collection.
   *
   * @param e The edge to add.
   * @return Status: ok or Status::InvalidOperation error.
   */
  Status AddEdge(const Edge& e) {
    // validate
    GAR_RETURN_NOT_OK(Validate(e));
    // add an edge
    IdType vertex_chunk_index = getVertexChunkIndex(e);
    edges_[vertex_chunk_index].push_back(e);
    num_edges_++;
    return Status::OK();
  }

  /**
   * @brief Get the current number of edges in the collection.
   *
   * @return The current number of edges in the collection.
   */
  IdType GetNum() const { return num_edges_; }

  /**
   * @brief Dump the collection into files.
   *
   * @return Status: ok or error.
   */
  Status Dump() {
    // construct the writer
    EdgeChunkWriter writer(edge_info_, prefix_, adj_list_type_);
    // construct empty edge collections for vertex chunks without edges
    IdType num_vertex_chunks =
        (num_vertices_ + vertex_chunk_size_ - 1) / vertex_chunk_size_;
    for (IdType i = 0; i < num_vertex_chunks; i++)
      if (edges_.find(i) == edges_.end()) {
        std::vector<Edge> empty_chunk_edges;
        edges_[i] = empty_chunk_edges;
      }
    // dump the offsets
    if (adj_list_type_ == AdjListType::ordered_by_source ||
        adj_list_type_ == AdjListType::ordered_by_dest) {
      for (auto& chunk_edges : edges_) {
        IdType vertex_chunk_index = chunk_edges.first;
        // sort the edges
        if (adj_list_type_ == AdjListType::ordered_by_source)
          sort(chunk_edges.second.begin(), chunk_edges.second.end(), cmp_src);
        if (adj_list_type_ == AdjListType::ordered_by_dest)
          sort(chunk_edges.second.begin(), chunk_edges.second.end(), cmp_dst);
        // construct and write offset chunk
        GAR_ASSIGN_OR_RAISE(
            auto offset_table,
            getOffsetTable(vertex_chunk_index, chunk_edges.second));
        GAR_RETURN_NOT_OK(
            writer.WriteOffsetChunk(offset_table, vertex_chunk_index));
      }
    }
    // dump the vertex num
    GAR_RETURN_NOT_OK(writer.WriteVerticesNum(num_vertices_));
    // dump the edge nums
    IdType vertex_chunk_num =
        (num_vertices_ + vertex_chunk_size_ - 1) / vertex_chunk_size_;
    for (IdType vertex_chunk_index = 0; vertex_chunk_index < vertex_chunk_num;
         vertex_chunk_index++) {
      if (edges_.find(vertex_chunk_index) == edges_.end()) {
        GAR_RETURN_NOT_OK(writer.WriteEdgesNum(vertex_chunk_index, 0));
      } else {
        GAR_RETURN_NOT_OK(writer.WriteEdgesNum(
            vertex_chunk_index, edges_[vertex_chunk_index].size()));
      }
    }
    // dump the edges
    for (auto& chunk_edges : edges_) {
      IdType vertex_chunk_index = chunk_edges.first;
      // convert to table
      GAR_ASSIGN_OR_RAISE(auto input_table, convertToTable(chunk_edges.second));
      // write table
      GAR_RETURN_NOT_OK(writer.WriteTable(input_table, vertex_chunk_index, 0));
      chunk_edges.second.clear();
    }
    is_saved_ = true;
    return Status::OK();
  }

 private:
  /**
   * @brief Construct an array for a given property.
   *
   * @param type The type of the property.
   * @param property_name The name of the property.
   * @param array The constructed array.
   * @param edges The edges of a specific vertex chunk.
   * @return Status: ok or Status::TypeError error.
   */
  Status appendToArray(const DataType& type, const std::string& property_name,
                       std::shared_ptr<arrow::Array>& array,  // NOLINT
                       const std::vector<Edge>& edges);

  /**
   * @brief Append the values for a propety for edges in a specific vertex
   * chunk into the given array.
   *
   * @tparam type The data type.
   * @param property_name The name of the property.
   * @param array The array to append.
   * @param edges The edges of a specific vertex chunk.
   * @return Status: ok or Status::ArrowError error.
   */
  template <Type type>
  Status tryToAppend(const std::string& property_name,
                     std::shared_ptr<arrow::Array>& array,  // NOLINT
                     const std::vector<Edge>& edges);

  /**
   * @brief Append the adj list for edges in a specific vertex chunk
   * into the given array.
   *
   * @param src_or_dest Choose to append sources or destinations.
   * @param array The array to append.
   * @param edges The edges of a specific vertex chunk.
   * @return Status: ok or Status::ArrowError error.
   */
  Status tryToAppend(int src_or_dest,
                     std::shared_ptr<arrow::Array>& array,  // NOLINT
                     const std::vector<Edge>& edges);

  /**
   * @brief Convert the edges in a specific vertex chunk into
   * an Arrow Table.
   *
   * @param edges The edges of a specific vertex chunk.
   */
  Result<std::shared_ptr<arrow::Table>> convertToTable(
      const std::vector<Edge>& edges);

  /**
   * @brief Construct the offset table if the adj list type is ordered.
   *
   * @param vertex_chunk_index The corresponding vertex chunk index.
   * @param edges The edges of a specific vertex chunk.
   */
  Result<std::shared_ptr<arrow::Table>> getOffsetTable(
      IdType vertex_chunk_index, const std::vector<Edge>& edges);

 private:
  EdgeInfo edge_info_;
  std::string prefix_;
  AdjListType adj_list_type_;
  std::unordered_map<IdType, std::vector<Edge>> edges_;
  IdType vertex_chunk_size_;
  IdType num_vertices_;
  IdType num_edges_;
  bool is_saved_;
};

}  // namespace builder
}  // namespace GAR_NAMESPACE_INTERNAL
#endif  // GAR_WRITER_EDGES_BUILDER_H_
